logger
======

logging server written on gevent


Run log server:
---------------
```
from netlog import Server
Server('./logs', 5010).start()
```


Usage from clients:
-------------------
```
from netlog import Client
client = Client('127.0.0.1', 5010, 'logname')
client.send('qwe asd')
client.send('ert \n dfg')   # may be multiline
client.close()              # or del client
```


Features:
---------

- put to one log file from many client processes
- save in binary format .tar.gz, use zcat and zgrep and for read
- unlimited size of log string
- rotation by date
- automatic delete old logs
