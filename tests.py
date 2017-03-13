#!/usr/bin/env python2.7

import unittest, time, os, shutil, datetime, gzip, random
from netlog import Logger, LogServer


class AppTest(unittest.TestCase):
    def setUp(self):
        self.port = random.randrange(7000, 8000)
        self.logsdir = 'netlog_test'
        self.date = datetime.datetime.now().date()
        self.date_str = str(self.date)

        self.server = LogServer(port=self.port, logsdir=self.logsdir,
                                max_lines=3)
        self.server.start()
        time.sleep(0.1)

    def test_main(self):
        # sendig messages from client
        logger = Logger('test0', '127.0.0.1', self.port, False)
        logger.log('qwe')
        logger.log('asd')
        logger.log('zxc')
        time.sleep(0.1)

        self.assertEqual(
            os.listdir(os.path.join(self.logsdir, 'test0')), [self.date_str])

        content = gzip.open(os.path.join(self.logsdir, 'test0',
                self.date_str)).read()
        self.assertEqual(content, 'qwe\nasd\nzxc\n')

    def tearDown(self):
        self.server.stop()
        time.sleep(0.1)
        shutil.rmtree(self.logsdir, True)


if __name__ == '__main__':
    unittest.main()
