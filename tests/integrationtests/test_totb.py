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
import multichain

logging.disable(logging.CRITICAL)


class TestTOTB(test_mixin.TestMixin, unittest.TestCase):
    def setUp(self):
        n_processes = 3
        self.broadcasts = []
        self.histories = []

        self.b = multichain.MultiChain(create=True)
        self.b._create()
        self.b._start()
        time.sleep(10)  # wait for boot up
        keypairs = [self.b._create_funded_keypair() for _ in range(n_processes)]

        for keypair, i in zip(keypairs, range(n_processes)):
            args = argparse.Namespace(
                protocol="totb",
                totb_privkey=keypair[0],
                totb_pubkeyhash=keypair[1],
                totb_prevtxhash=keypair[2],
                multichain_chainname=self.b.getinfo()["nodeaddress"],
                multichain_create=True,
            )
            tpb = tamperproofbroadcast.TamperProofBroadcast._Init(args)
            tpb._create()
            tpb._start()
            self.broadcasts.append(tpb)
            history = []
            self.histories.append(history)
        time.sleep(10)  # wait for boot up

    def tearDown(self):
        for bc in self.broadcasts:
            bc._stop()
            bc._uncreate()
        for history in self.histories:
            del history
        self.b._stop()
        self.b._uncreate()

    def test_total_order(self):
        self.total_order(test_time=60)

    def test_fifo_order(self):
        self.fifo_order(test_time=60)

    def test_no_creation(self):
        self.no_creation(test_time=60)

    def test_no_duplication(self):
        self.no_duplication(test_time=60)
