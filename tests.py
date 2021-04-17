import unittest
import os
import sqlite3
from main import scheduler

class TestStringMethods(unittest.TestCase):
    def testSetupDB(self):
        s = scheduler()
        conn = sqlite3.connect('test.db')
        s.setupDB(conn)
        self.assertTrue(os.path.isfile("./test.db"))

    def testAddJob(self):
        s = scheduler()
        conn = sqlite3.connect('test.db')
        s.addJob(conn, "test-job","3s", "1hr", "./hello.py")
        self.assertTrue(os.path.isfile("./logs/test-job.txt"))

    def testCalculateSeconds(self):
        s = scheduler()
        conn = sqlite3.connect('test.db')
        v = s.calculateSeconds("1hr 30m 10s")
        self.assertEqual(v, 5410)
        v = s.calculateSeconds("random string")
        self.assertEqual(v, -1)
        v = s.calculateSeconds("10m")
        self.assertEqual(v, 600)
        v = s.calculateSeconds("10mm")
        self.assertEqual(v, -1)
        v = s.calculateSeconds("5s")
        self.assertEqual(v, 5)
        v = s.calculateSeconds("5 s")
        self.assertEqual(v, -1)
        v = s.calculateSeconds("1hr 1hr")
        self.assertEqual(v, -1)




if __name__ == '__main__':
    unittest.main()