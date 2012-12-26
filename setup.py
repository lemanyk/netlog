# coding: utf-8

from distutils.core import setup


long_description = r'''
logger
======

logging server written on gevent

Run log server:
---------------

::

    from netlog import Server
    Server('./logs', 5010).start()

If you don’t need blocking in .start() line:

::

    Server('./logs', 5010).start(blocking=False)

Simple way to run as daemon:

::

    python -c "import netlog; netlog.Server('./logs', 5010').start()" &

Usage from clients:
-------------------

::

    from netlog import Client
    client = Client('127.0.0.1', 5010, 'logname')
    client.send('qwe asd')
    client.send('ert\n dfg')    # may be multiline
    client.close()              # or del client

Features:
---------

-  put to one log file from many client processes
-  save in binary format .tar.gz, use zcat and zgrep for read
-  unlimited size of log string
-  rotation by date
-  automatic delete old logs

TODO:
-----

-  realize rotator :)
-  fetch Ctrl+C and -9 signals for flush before exit
-  udp transfer (maybe, only after v1.0)
-  implement logging.handlers.SocketHandler protocol (maybe, only after
   v1.0)
'''


setup(
    name='netlog',
    version='0.5.5',
    py_modules=['netlog'],
    url='https://github.com/lemanyk/netlog',
    download_url='https://github.com/lemanyk/netlog/',
    description='logging stream server written on gevent',
    long_description=long_description,
    author='lemanyk',
    author_email='lemanyk@gmail.com',
    install_requires=['gevent'],
    license='MIT',
    classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Programming Language :: Python',
    ],
)
