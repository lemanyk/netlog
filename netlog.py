import os
import sys
import socket
import asyncore
import signal
import gzip
from datetime import datetime, timedelta


__all__ = ['Logger', 'LogServer']


class Logger(object):
    """
    client for logging server

    usage:
        logger = Logger('127.0.0.1', 5010, 'filename')
        logger.log('qwe asd')

    :param host: host to connect
    :param port: port to connect
    :param filename: file to write
    :param log_datetime=True: put current datetime to the log
    """

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, filename, host, port=7020, log_datetime=True):
        self.filename = filename
        self.host = host
        self.port = port
        self.log_datetime = log_datetime
        self._connect()

    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except socket.error:
            pass    # do nothing if the logging server is not launched

    def log(self, string):
        """send the string to the logging server"""
        string = str(string).replace('\n', ' ')     # no \n allowed

        if self.log_datetime:
            string = '%s %s' % (datetime.now().strftime(
                                self.DATETIME_FORMAT), string)

        try:
            self.sock.send('%s %s\n' % (self.filename, string))
        except socket.error:
            pass

    def __del__(self):
        try:
            self.sock.close()
        except socket.error:
            pass


class LogServer(object):
    """
    server process
    listens to specified port for connections

    usage:
        Server('logs', 5010).start()

    :param path: directory to save logs
    :param port=7020: tcp port to listen to
    :param host='0.0.0.0': host to listen to
    :param archive=True: put into .tar.gz file or into plain text file if False
        type 'zcat/zmore/zless/zgrep filename.tar.gz' to open an archive
    :param max_lines=MAX_LINES: maximum amount of lines to keep in memory
        before flushing them into the disk
    :param lifetime=LIFETIME: maximum days before deleting old logs
    """

    BUF_SIZE = 1024 * 4
    TERMINATOR = '\n'
    debug = False

    class Server(asyncore.dispatcher):
        """Listen for connections"""
        def __init__(self, logserver):
            asyncore.dispatcher.__init__(self)
            self.logserver = logserver
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((logserver.host, logserver.port))
            self.listen(5)

        def handle_accept(self):
            pair = self.accept()
            if pair is not None:
                sock, addr = pair
                self.logserver.Handler(sock, self.logserver)

    class Handler(asyncore.dispatcher_with_send):
        """Request handler"""
        def __init__(self, sock, logserver):
            asyncore.dispatcher_with_send.__init__(self, sock)
            self.logserver = logserver
            self.buf = ''
            
        def handle_read(self):
            self.buf += self.recv(512)
            while '\n' in self.buf:
                line, self.buf = self.buf.split('\n', 1)
                self.logserver.add(line)

    def __init__(self, host='0.0.0.0', port=7020, logsdir='~/netlog_logs',
                 archive=True, max_lines=1000, lifetime=30,
                 pidfile=None):
        self.host = host
        self.port = port
        self.logsdir = os.path.expanduser(logsdir)
        self.archive = archive
        self.max_lines = max_lines
        self.lifetime = lifetime
        self.pidfile = pidfile or '/var/run/user/%s/netlog.pid' % os.geteuid()
        self.open = gzip.open if self.archive else open

    def start(self, daemon=True):
        """Start logging daemon"""
        if daemon:
            self._become_daemon()
        signal.signal(signal.SIGTERM, self.stop)  # signal 15 (kill)
        signal.signal(signal.SIGINT, self.stop)   # signal 2 (ctrl+c)

        self.logs = {}
        self.count = 0
        self.date = str(datetime.now().date())
        self.server = self.Server(self)
        asyncore.loop()

    def _become_daemon(self):
        #if os.fork() > 0: sys.exit()
        #if os.fork() > 0: sys.exit()
        try:
            old_pid = int(open(self.pidfile).read())
            os.getpgid(old_pid)
            raise Exception('Logger daemon is already running with pid %d!'
                            % old_pid)
        except (OSError, IOError):
            pass
        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

    def stop(self, signum, frame):
        """Close socket, flush logs into disk"""
        self.server.close()
        self.flush()
        os.remove(self.pidfile)
        sys.exit()

    def add(self, line):
        """Add new line into buffer"""
        if self.count % 100 == 0 and self.date != str(datetime.now().date()):
            self.flush()
            for logfile in self.logs:
                # removing old logs
                for_del_log = os.path.join(self.logsdir, logfile,
                        str((datetime.now()-timedelta(days=self.lifetime)).date()))
                if os.path.exists(for_del_log):
                    os.remove(for_del_log)

            self.date = str(datetime.now().date())

        if line:
            filename, string = line.split(' ', 1)
            self.logs.setdefault(filename, '')
            self.logs[filename] += string + '\n'
            self.count += 1
            if self.count > self.max_lines:
                self.flush()

    def flush(self):
        """Write logs into disk"""
        for filename in self.logs.keys():
            logdir = os.path.join(self.logsdir, filename)
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            self.open(os.path.join(logdir, self.date), 'a').write(
                      self.logs[filename])
            del self.logs[filename]

        self.count = 0
