import logging.config
import logging
import threading
import time
import hashlib
import os
import module
import etcd
import fifoorderbroadcast
import multichain

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("tamperproofbroadcast")


class HTLLBroadcast(module.Module):
    def __init__(self, fifoprivkey=None, fifopubkeyhash=None, fifoprevtxhash=None, fifoqueuesize=2**10, etcdhost=None, etcdport=None, etcdqueuesize=128, etcdbatchsize=128):
        self.privkey = fifoprivkey
        self.pubkeyhash = fifopubkeyhash
        self.prevtxhash = fifoprevtxhash
        self.etcdbroadcast = etcd.ETCD(
            host=etcdhost,
            port=etcdport,
            queuesize=etcdqueuesize,
            batchsize=etcdbatchsize,
        )
        self.log = []
        self.map = {}
        self.mth = hashlib.sha256()
        self.n = 0
        self.stop_event = threading.Event()

    def broadcast(self, message):
        msg = (self.pubkeyhash, 0, message)
        logger.info("broadcast: message=%s", msg)
        return self.etcdbroadcast.broadcast(msg)

    def deliver(self):
        msg = self.etcdbroadcast.deliver()
        logger.info("deliver: message=%s" % (msg,))
        self.log.append(msg)
        self.mth.update(self._pack(msg).encode())
        self.n = self.n + 1
        return msg

    def _timeout_anchor(self):
        while not self.stop_event.is_set():
            message = (self.n, self.mth.digest())
            logger.info("anchoring: message=%s" % (message,))
            self.southbound.broadcast(message)
            try:
                for _ in range(128):
                    m = self.southbound.deliver()
                    self.map[m[0]] = m[1]
            except:
                pass
            time.sleep(5)


    def _start(self):
        self.etcdbroadcast._start()
        threading.Thread(target=self._timeout_anchor, daemon=True).start()

    def _stop(self):
        self.stop_event.set()
        self.etcdbroadcast._stop()

    def _create(self):
        self.etcdbroadcast._create()

    def _uncreate(self):
        self.etcdbroadcast._uncreate()
#
# import time
#
# b = multichain.MultiChain()
#
#
# b._create()
# b._start()
# keypair = b._create_funded_keypair()
#
# fifob = fifoorderbroadcast.FIFOOrderBroadcast(keypair[0], keypair[1], keypair[2])
# htllb = HTLLBroadcast()
#
# fifob._register_southbound(b)
# fifob._register_northbound(htllb)
# htllb._register_southbound(fifob)
#
#
# fifob._create()
# fifob._start()
#
# htllb._create()
# htllb._start()
#
# for i in range(2**10):
#     htllb.broadcast(i)
# time.sleep(10)
# for i in range(2**10):
#     htllb.deliver()
