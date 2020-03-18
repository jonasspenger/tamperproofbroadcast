import multiprocessing
import logging.config
import threading
import binascii
import logging
import pickle
import queue
import etcd3
import os
import module
import time
import inspect

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("etcdbroadcast")


class ETCDBroadcast(module.Module):
    def __init__(self, host="localhost", port="2379", queuesize=128):
        self.etcdclient = etcd3.client(host=host, port=port, grpc_options={'grpc.max_send_message_length': 2**30,}.items())
        self.queue = queue.Queue(maxsize=queuesize)
        self.cancel = None

    def broadcast(self, message):
        self.etcdclient.put("broadcast", self._pack(message))

    def deliver(self):
        try:
            return self.queue.get_nowait()
        except:
            raise Exception("nothing to deliver")

    def _deliver(self):
        try:
            iter, self.cancel = self.etcdclient.watch("broadcast", start_revision=1)
            for i, message in enumerate(iter):
                self.queue.put(self._unpack(message._event.kv.value))
            self.cancel()
        except etcd3.exceptions.RevisionCompactedError as e:
            iter, self.cancel = self.etcdclient.watch(
                "broadcast", start_revision=e.compacted_revision
            )
            for i, message in enumerate(iter):
                self.queue.put(self._unpack(message._event.kv.value))
            self.cancel()

    def _start(self):
        threading.Thread(target=self._deliver, daemon=True).start()

    def _stop(self):
        self.cancel()
