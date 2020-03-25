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
import etcd

logging.disable(logging.CRITICAL)

class TestFOTB(unittest.TestCase):
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
                protocol="fotb",
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

    def test_fifo_order(self):
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
        # check each history was delivered in FIFO order with increasing message number (i)
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                seqnums = [msg[2] for msg in pid_history]
                self.assertTrue(all(seqnums[i] < seqnums[i+1] for i in range(len(seqnums)-1)))