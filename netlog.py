from SocketServer import ThreadingTCPServer, StreamRequestHandler
import threading
import socket
import time
from Queue import Queue
import os
import datetime
import gzip
import signal


__all__ = ['Server', 'Client']


class Server(object):
    """
    server process
    listen specified port for connections

    usage:
        Server('/logs', 5010).start()

    :param path: directory to save logs
    :param port: tcp port to listen
    :param host='0.0.0.0': host for listen
    :param binary=True: put into .tar.gz file or into plain text file
    :param max_count=MAX_COUNT: maximum strings in memory before flush to files
    :param life_time=LIFE_TIME: maximum days before delete log file
    :param terminator=TERMINATOR: terminator between log strings
    """

    BUF_SIZE = 1024 * 4
    MAX_COUNT = 1000        # max lines before flush
    LIFE_TIME = 30          # count of days for save files
    TERMINATOR = '\n'
    debug = False

    class Handler(StreamRequestHandler):
        def handle(self):
            self.server._server.handle(self.request)

    def __init__(self, path, port, host='0.0.0.0', binary=True,
            max_count=MAX_COUNT, life_time=LIFE_TIME, terminator=TERMINATOR):
        self.path = path
        self.port = port
        self.host = host
        self.binary = binary
        self.max_count = max_count
        self.life_time = life_time
        self.terminator = terminator

        self.dirs_file = os.path.join(self.path, 'netlog_dirs')
        self.open = gzip.open if self.binary else open

    def start(self, debug=False):
        """
        start serving
        :param debug: if True then write self work info into 'netlog' log
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(self.dirs_file):
            open(self.dirs_file, 'w')

        self.debug = debug
        self.debug_log('start on %s %s' % (self.host, self.port))

        self.queue = Queue()
        self.stopping = threading.Event()

        signal.signal(signal.SIGTERM, self.stop)  # signal 15 (kill)
        signal.signal(signal.SIGINT, self.stop)   # signal 2 (ctrl+c)

        threading.Thread(target=self.flusher).start()
        threading.Thread(target=self.rotator).start()

        self.server = ThreadingTCPServer((self.host, self.port), self.Handler)
        self.server._server = self
        self.server.serve_forever()

    def handle(self, connection):
        """work with connection, in dedicated thread"""
        self.debug_log('connect with %s' % connection)
        buf = ''
        logfile = None
        buf_partial = False
        while not self.stopping.is_set():
            # recv data
            parts = buf.split(' ', 2)
            if len(parts) < 3 or buf_partial:
                buf += connection.recv(self.BUF_SIZE)   # blocking
                buf_partial = False
                continue

            # parse data
            self.debug_log('buffer', connection, parts)
            count, action, buf = parts
            try:
                count = int(count)
            except:
                print 444, parts
                assert 0
            print 222, count, action, len(buf)
            if len(buf) < count:
                buf_partial = True
                print 333
                continue

            string = buf[:count]
            buf = buf[count:]
            if action in ['m', 't']:
                self.queue.put((logfile, action, string))
            elif action == 'f':
                logfile = string

    def flusher(self):
        """flusher process, flush memory data to logs """
        logs = {}
        count = 0

        while True:
            # wait and get new message
            log_dir, action, string = self.queue.get()
            self.debug_log('queue', repr(log_dir), repr(action), repr(string))

            # parse message
            log = logs.setdefault(log_dir, {})
            if action == 'm':
                count += 1
                log.setdefault('strings', []).append(string)
            elif action == 't':
                log['terminator'] = string
            
            # flush to files
            if count >= self.max_count or self.stopping.is_set():
                self.debug_log('flush', logs.keys())
                date_str = str(datetime.datetime.now().date())
                for log_dir, log in logs.items():
                    path = os.path.join(self.path, log_dir)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    terminator = log.get('terminator', self.terminator)
                    with self.open(os.path.join(path, date_str), 'a') as f:
                        f.write(terminator.join(log['strings']))
                        f.write(terminator)
                        f.flush()

                # register dirs in rotator
                reg_logs = open(self.dirs_file).read().split('\n')
                reg_logs_new = [log for log in reg_logs if os.path.exists(log)]
                for log in reg_logs:
                    if log not in reg_logs_new:
                        reg_logs_new.append(log)
                if reg_logs_new != reg_logs:
                    open(self.dirs_file, 'w').write('\n'.join(reg_logs_new))

                logs = {}
                count = 0

            if self.stopping.is_set():
                break

    def rotator(self):
        """rotation process"""
        date = datetime.datetime.now().date()
        while not self.stopping.is_set():
            time.sleep(0.1)
            cur_date = datetime.datetime.now().date()

            if date != cur_date:
                logs = open(self.dirs_file).read().split('\n')
                self.debug_log('rotate:', logs)

                date_str = str(date)
                cur_date_str = str(cur_date)
                del_date_str = str(cur_date - datetime.timedelta(
                        days=self.life_time))

                for log in logs:
                    logfile_src = os.path.join(log, date_str)
                    logfile_dst = os.path.join(log, cur_date_str)
                    logfile_del = os.path.join(log, del_date_str)
                    if os.path.exists(logfile_src):
                        os.move(logfile_src, logfile_dst)
                    if os.path.exists(logfile_del):
                        os.remove(logfile_del)

                self.date = datetime.now().date()

    def stop(self, signum, frame):
        self.debug_log('stopping')
        self.stopping.set()
        del self.server
        self.debug_log('stopped, seeya!')

    def debug_log(self, *strings):
        """print self log strings"""
        if self.debug:
            string = ' '.join(map(str, strings))
            self.open(os.path.join(self.path, 'netlog'), 'a')\
                    .write('%s\n' % string)


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
    :param filename: file to write
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
