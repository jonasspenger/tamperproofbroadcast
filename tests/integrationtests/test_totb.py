import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import unittest.mock
import unittest
import argparse
import logging
import time
import tamperproofbroadcast
import multichain

logging.disable(logging.CRITICAL)

class TestTOTB(unittest.TestCase):
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
            keypair
            args = argparse.Namespace(
                protocol="totb",
                fotb_privkey=keypair[0],
                fotb_pubkeyhash=keypair[1],
                fotb_prevtxhash=keypair[2],
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
        # check shortest history is equal to prefix of other histories
        for els in zip(*self.histories):
            e = els[0]
            for el in els:
                self.assertEqual(e, el)
