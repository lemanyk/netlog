import os
from gevent import server, socket, sleep, queue, spawn


class Server(object):
    """
    server process
    while started listen specified port for connections
    after every MAX_COUNT requests flushe to files

    usage:
        Server('/logs', 5010).start()

    :param path: directory to save logs
    :param port: tcp port to listen
    """
    BUF_SIZE = 1024 * 4
    MAX_COUNT = 1000        # max lines before flush
    LIFE_TIME = 30          # count of days for save files
    TERMINATOR = '\n'

    def __init__(self, path, port, host='0.0.0.0'):
        self.path = path
        self.port = port
        self.host = host
        self.queue = queue.Queue()

    def start(self, blocking=True):
        """
        start serving
        :param blocking: if True then code blocked in Server(..).start() line
        """
        print 'start on %s %s' % (self.host, self.port)
        spawn(self.flusher)
        spawn(self.rotator)
        self._start() if blocking else spawn(self._start)

    def _start(self):
        self.server = server.StreamServer((self.host, self.port), self.handle)
        self.server.serve_forever()

    def flusher(self):
        """flusher process, flushe memory data to logs """
        logfiles = {}
        count = 0

        while True:
            # wait and get new message
            logfile, action, string = self.queue.get()
            print 'queue', repr(logfile), repr(action), repr(string)

            # parse message
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
                    terminator = logitem.get('terminator', self.TERMINATOR)
                    with open(path, 'a') as f:
                        f.write(terminator.join(logitem['strings']))
                        f.write(terminator)

                logfiles = {}
                count = 0

    def rotator(self):
        """rotation process"""
        while True:
            sleep(600)

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
    client for logger server

    usage:
        client = Client('127.0.0.1', 5010, 'filename')
        client.send('qwe asd')

        client.set_terminator('\n----------\n\n')
        client.send('rty\n fgh')

    :param port: port to connect
    :param host: host to connect
    "param filename: file to write
    """
    def __init__(self, port, host, filename):
        self.sock = socket.socket()
        self.sock.connect((port, host))
        self.set_filename(filename)

    def set_filename(self, filename):
        """set name of file or dir to write log strings"""
        self.send('f %s' % filename, True)

    def set_terminator(self, terminator):
        """set string, which will be between log strings"""
        self.send('t %s' % terminator, True)

    def send(self, string, control=False):
        """send string to server for write to log file"""
        if not control:
            string = 'm %s' % string
        string = '%d %s' % (len(string)-2, string)
        self.sock.send(string)

    def close(self):
        self.sock.close()

    def __del__(self):
        self.close()
