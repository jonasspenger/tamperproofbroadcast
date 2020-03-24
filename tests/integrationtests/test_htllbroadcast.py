import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../tamperproofbroadcast"))

import unittest.mock
import unittest
import logging
import time
import fifoorderbroadcast
import htllbroadcast
import multichain
import etcd

logging.disable(logging.CRITICAL)


class TestHTLLBroadcast(unittest.TestCase):
    def setUp(self):
        n_blockchains = 3
        self.blockchains = []
        self.fifobroadcasts = []
        self.broadcasts = []
        self.northbounds = []

        b = multichain.MultiChain()
        b._create()
        b._start()
        self.blockchains.append(b)

        e = etcd.ETCD()
        e._create()
        e._start()

        keypairs = [b._create_funded_keypair() for _ in range(n_blockchains)]

        for i in range(n_blockchains - 1):
            b2 = multichain.MultiChain(chainname=b.getinfo()["nodeaddress"])
            b2._create()
            b2._start()
            self.blockchains.append(b2)

        for keypair, b in zip(keypairs, self.blockchains):
            bc = fifoorderbroadcast.FIFOOrderBroadcast(
                keypair[0], keypair[1], keypair[2]
            )
            northbound = unittest.mock.MagicMock()
            self.northbounds.append(northbound)
            bc._register_southbound(b)
            bc._register_northbound(northbound)
            self.fifobroadcasts.append(bc)
            hb = htllbroadcast.HTLLBroadcast(
                keypair[0], keypair[1], keypair[2], 2 ** 10, e.host, e.port, 128, 128
            )
            hb._register_southbound(bc)
            bc._register_northbound(hb)
            bc._create()
            bc._start()
            hb._start()
            self.broadcasts.append(hb)

        time.sleep(5)

    def tearDown(self):
        for bc in self.broadcasts:
            bc._uncreate()
            bc._stop()
        for bc in self.fifobroadcasts:
            bc._uncreate()
            bc._stop()
        for b in self.blockchains:
            b._uncreate()
            b._stop()

    # def test_fifo_order(self):
    #     n_messages = 2 ** 10
    #     for i in range(n_messages):
    #         for bc in self.broadcasts:
    #             bc.broadcast(i)
    #
    #     time.sleep(60)
    #
    #     for nb in self.northbounds:
    #         for bc in self.broadcasts:
    #             pid = bc.pubkeyhash
    #             calls = [
    #                 c[0][2] for c in nb._upon_deliver.call_args_list if c[0][0] == pid
    #             ]
    #             issorted = all(calls[i] <= calls[i + 1] for i in range(len(calls) - 1))
    #             self.assertTrue(issorted)
    #             self.assertTrue(len(calls) > 0)
    #
    # def test_total_order(self):
    #     n_messages = 2 ** 10
    #     for i in range(n_messages):
    #         for bc in self.broadcasts:
    #             bc.broadcast(i)
    #
    #     time.sleep(60)
    #
    #     for nb1 in self.northbounds:
    #         for nb2 in self.northbounds:
    #             nb1calls = [call for call in nb1._upon_deliver.call_args_list]
    #             nb2calls = [call for call in nb2._upon_deliver.call_args_list]
    #             nb1callsintersect = [call for call in nb1calls if call in nb2calls]
    #             nb2callsintersect = [call for call in nb2calls if call in nb1calls]
    #             self.assertEqual(nb1callsintersect, nb2callsintersect)
    #
    #     for nb in self.northbounds:
    #         self.assertTrue(len(nb._upon_deliver.call_args_list) > 0)
    #
    def test_validity(self):
        n_messages = 2 ** 8

        # broadcast
        print("broadcast")
        for i in range(n_messages):
            for bc in self.broadcasts:
                bc.broadcast(i)

        # synchronize
        print("synchronize")
        t = time.time()
        while time.time() < t + 10:
            for (nb, bc) in zip(self.northbounds, self.broadcasts):
                try:
                    msg = bc.deliver()
                    nb._upon_deliver(*msg)
                except:
                    pass

        # check
        print("check")
        for nb in self.northbounds:
            for bc in self.broadcasts:
                pid = bc.pubkeyhash
                for i in range(n_messages):
                    nb._upon_deliver.assert_any_call(pid, unittest.mock.ANY, i)

        # n_messages = 2 ** 10
        # for i in range(n_messages):
        #     for bc in self.broadcasts:
        #         bc.broadcast(i)
        #
        # time.sleep(60)
        #
        # for nb in self.northbounds:
        #     for bc in self.broadcasts:
        #         pid = bc.pubkeyhash
        #         for i in range(n_messages):
        #             nb._upon_deliver.assert_any_call(pid, unittest.mock.ANY, i)

    #
    # def test_agreement(self):
    #     n_messages = 2 ** 10
    #     for i in range(n_messages):
    #         for bc in self.broadcasts:
    #             bc.broadcast(i)
    #
    #     time.sleep(60)
    #
    #     for nb1 in self.northbounds:
    #         for nb2 in self.northbounds:
    #             for call in nb2._upon_deliver.call_args_list:
    #                 nb1._upon_deliver.assert_any_call(*call[0])
