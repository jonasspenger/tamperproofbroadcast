import multiprocessing
import threading
import binascii
import pickle
import queue
import etcd3
import os
import module
import time
import inspect

class ETCDBroadcast(module.Module):
    def _pack(self, message):
        return binascii.hexlify(pickle.dumps(message)).decode()

    def _unpack(self, payload):
        return pickle.loads(binascii.unhexlify(payload))

    def __init__(self, host="localhost", port="2379"):
        self.etcdclient = etcd3.client(host=host, port=port)

    def broadcast(self, message):
        # returns LSN
        packedmsg = self._pack(message)
        return self.etcdclient.put('broadcast', packedmsg).header.revision

    def deliver(self, lsn):
        # returns LSN, message
        iter, cancel = self.etcdclient.watch('broadcast', start_revision=lsn)
        for i, message in enumerate(iter):
            break
        cancel()
        return message._event.kv.mod_revision, message._event.kv.value
