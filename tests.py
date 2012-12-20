import gevent
from netlog import Server, Client


gevent.spawn(lambda: Server('./logs', 5000).start())
gevent.sleep(1)

client = Client('127.0.0.1', 5000, 'test0')
client.send('asd xvb')
client.send('asd\nxvb')
client.close()
