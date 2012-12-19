from gevent.server import StreamServer


class Server(StreamServer):
    """
    """
    def __init__(self, port, host='0.0.0.0'):
        self.port = port
        self.host = host

    def start(self):
        print 'start on %s %s' % (self.host, self.port)
        self.server = StreamServer((self.host, self.port), self.handle)
        self.server.serve_forever()

    def handle(self, sock, addr):
        pass
    
    def stop(self):
        print 'seeya!'
