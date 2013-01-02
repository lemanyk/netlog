#!/usr/bin/env python2

import unittest, multiprocessing, time, os, shutil, datetime, gzip, random
from netlog import Server, Client
import pdb
d = pdb.set_trace

class AppTest(unittest.TestCase):
    def setUp(self):
        self.path = 'logs'
        self.port = random.randrange(5000, 6000)
        self.date = datetime.datetime.now().date()
        self.date_str = str(self.date)
        shutil.rmtree(self.path, True)

        # start server
        def start_server():
            try:
                Server(self.path, self.port, max_count=3).start(True)
            except Exception:
                pass
        self.server = multiprocessing.Process(target=start_server)
        self.server.start()

    def test_main(self):
        time.sleep(0.1)
        self.assertEqual(os.listdir(self.path), ['netlog_dirs', 'netlog'])

        # send messages from clients
        client = Client('127.0.0.1', self.port, 'test0')
        client.send('qwe')
        client.send('asd')
        time.sleep(0.1)
        self.assertEqual(os.listdir(self.path), ['netlog_dirs', 'netlog'])

        client.send('zxc')
        time.sleep(0.1)
        self.assertEqual(os.listdir(self.path),
                ['netlog_dirs', 'netlog', 'test0'])

        self.assertEqual(os.listdir(os.path.join(self.path, 'test0')),
                [self.date_str])
        content = gzip.open(os.path.join(self.path, 'test0',
                str(self.date))).read()
        self.assertEqual(content, 'qwe\nasd\nzxc\n')

    def tearDown(self):
        self.server.terminate()
        self.server.join()
        #del self.server


if __name__ == '__main__':
    unittest.main()
