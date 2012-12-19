from gevent.server import StreamServer


class Server(StreamServer):
    """
    """
    BUF_SIZE = 1024 * 4

    def __init__(self, port, host='0.0.0.0'):
        self.port = port
        self.host = host

    def start(self):
        print 'start on %s %s' % (self.host, self.port)
        self.server = StreamServer((self.host, self.port), self.handle)
        self.server.serve_forever()

    def handle(self, sock, addr):
        buf = sock.read(self.BUF_SIZE)
        file_name, buf = buf.split('\n', 1)
        while True:
            buf = sock.read(self.BUF_SIZE)
    
    def stop(self):
        print 'seeya!'
