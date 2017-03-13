logger
======

logging server written on pure python


Run log server:
---------------
```
from netlog import Server
Server('./logs', 5010).start()
```

Params:
* path - directory for logs
* port - listen tcp port
* host='0.0.0.0' - listen host

If you don't need blocking in .start() line:
```
Server('./logs', 5010).start(blocking=False)
```

Simple way to run as daemon:
```
python -c "import netlog; netlog.Server('./logs', 5010').start()" &
```


Usage from clients:
-------------------
```
from netlog import Client
client = Client('127.0.0.1', 5010, 'logname')
client.send('qwe asd')
client.close()              # or del client
```

Params:
* host - host, where is log server runned
* port - tcp port for connect
* filename - file to write log strings

Features:
---------

* put to one log file from many client processes
* save in binary format .tar.gz, use zcat and zgrep for read
* unlimited size of log string
* rotation by date
* automatic delete old logs


TODO:
-----
+ realize rotator and binary logs :)
+ fetch Ctrl+C and -9 signals for flush before exit
+ udp transfer (maybe, only after v1.0)
+ implement logging.handlers.SocketHandler protocol (maybe, only after v1.0)
