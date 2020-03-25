import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import unittest.mock
import unittest
import argparse
import logging
import time
import tamperproofbroadcast
import etcd

logging.disable(logging.CRITICAL)

class TestHTLLTBTEST(unittest.TestCase):
    def setUp(self):
        n_processes = 3
        self.broadcasts = []
        self.histories = []

        self.e = etcd.ETCD(create=True)
        self.e._create()

        for _ in range(n_processes):
            args = argparse.Namespace(
                protocol="htlltbtest",
                etcd_port=self.e.port,
            )
            tpb = tamperproofbroadcast.TamperProofBroadcast._Init(args)
            tpb._create()
            tpb._start()
            self.broadcasts.append(tpb)
            history = []
            self.histories.append(history)

    def tearDown(self):
        for bc in self.broadcasts:
            bc._stop()
            bc._uncreate()
        for history in self.histories:
            del history
        self.e._uncreate()

    def test_total_order(self):
        test_time = 60

        # broadcast and deliver for test_time seconds
        t0 = time.time()
        i = 0
        while time.time() < t0 + test_time:
            for bc, hi in zip(self.broadcasts, self.histories):
                bc.broadcast(i)
                try:
                    for _ in range(2**10):
                        hi.append(bc.deliver())
                except:
                    pass
            i = i + 1

        # check all histories longer than 0
        for hi in self.histories:
            self.assertTrue(len(hi) > 0)
        # check history from other pids longer than 0
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                self.assertTrue(len(pid_history) > 0)
        # check shortest history is equal to prefix of other histories
        for els in zip(*self.histories):
            e = els[0]
            for el in els:
                self.assertEqual(e, el)
