import os
from gevent import server, socket, sleep, queue, spawn


class Server(object):
    """
    """
    BUF_SIZE = 1024 * 4
    MAX_COUNT = 3

    def __init__(self, path, port, host='0.0.0.0'):
        self.path = path
        self.port = port
        self.host = host
        self.queue = queue.Queue()

    def start(self):
        print 'start on %s %s' % (self.host, self.port)
        spawn(self.flusher)
        self.server = server.StreamServer((self.host, self.port), self.handle)
        self.server.serve_forever()

    def flusher(self):
        logfiles = {}
        count = 0

        while True:
            # wait and get new message
            logfile, action, string = self.queue.get()
            print 'queue', repr(logfile), repr(action), repr(string)

            #
            log = logfiles.setdefault(logfile, {})
            if action == 'm':
                count += 1
                log.setdefault('strings', []).append(string)
            elif action == 't':
                log['terminator'] = string
            
            # flush to files
            if count >= self.MAX_COUNT:
                print 'flush', logfiles
                for logfile, logitem in logfiles.items():
                    path = os.path.join(self.path, logfile)
                    try:
                        os.makedirs(self.path)
                    except OSError:
                        pass
                    terminator = logitem.get('terminator', '\n')
                    with open(path, 'a') as f:
                        f.write(terminator)
                        f.write(terminator.join(logitem['strings']))

                logfiles = {}
                count = 0

    def handle(self, sock, addr):
        print 'connect with %s %s' % addr
        buf = ''
        logfile = None
        while True:
            # recv data
            buf += sock.recv(self.BUF_SIZE)
            parts = buf.split(' ', 2)

            # parse data
            if len(parts) == 3:
                print 'buffer', addr, parts
                count, action, buf = parts
                count = int(count)          # danger
                string = buf[:count]
                buf = buf[count:]
                if action in ['m', 't']:
                    self.queue.put((logfile, action, string))
                elif action == 'f':
                    logfile = string
            else:
                sleep(2)

    def stop(self):
        print 'seeya!'


class Client(object):
    """
    """
    def __init__(self, port, host, logfile):
        self.sock = socket.socket()
        self.sock.connect((port, host))
        self.send('f %s' % logfile, True)

    def send(self, string, control=False):
        if not control:
            string = 'm %s' % string
        string = '%d %s' % (len(string)-2, string)
        self.sock.send(string)

    def close(self):
        self.sock.close()

    def __del__(self):
        self.close()
