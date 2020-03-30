import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.append(os.path.join(os.path.dirname(__file__)))

import unittest.mock
import unittest
import argparse
import logging
import time
import tamperproofbroadcast
import test_mixin
import etcd


logging.disable(logging.CRITICAL)


class TestHTLLTBTEST(test_mixin.TestMixin, unittest.TestCase):
    def setUp(self):
        n_processes = 3
        self.broadcasts = []
        self.histories = []

        self.e = etcd.ETCD(create=True)
        self.e._create()

        for _ in range(n_processes):
            args = argparse.Namespace(protocol="htlltbtest", etcd_port=self.e.port,)
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
        self.total_order(test_time=10)

    def test_fifo_order(self):
        self.fifo_order(test_time=10)

    def test_no_creation(self):
        self.no_creation(test_time=10)

    def test_no_duplication(self):
        self.no_duplication(test_time=10)
