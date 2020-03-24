import multiprocessing
import logging.config
import threading
import backoff
import tempfile
import binascii
import logging
import pickle
import shutil
import queue
import port_for
import etcd3
import os
import module
import time
import inspect

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("etcd")


class _ETCDBroadcast(module.Module):
    def __init__(self, host="localhost", port="2379", queuesize=128):
        self.host = host
        self.port = port
        self.queuesize = queuesize
        self.queue = queue.Queue(maxsize=queuesize)
        self.cancel = None

    @backoff.on_exception(backoff.expo, Exception)
    def broadcast(self, message):
        self.etcdclient.put("broadcast", self._pack(message))

    def deliver(self):
        try:
            return self.queue.get_nowait()
        except:
            raise Exception("nothing to deliver")

    def _deliver(self, start_revision=1):
        try:
            try:
                iter, self.cancel = self.etcdclient.watch(
                    "broadcast", start_revision=start_revision
                )
                for i, message in enumerate(iter):
                    self.queue.put(self._unpack(message._event.kv.value))
                    start_revision = message._event.kv.mod_revision + 1
                self.cancel()
            except etcd3.exceptions.RevisionCompactedError as e:
                iter, self.cancel = self.etcdclient.watch(
                    "broadcast", start_revision=e.compacted_revision
                )
                for i, message in enumerate(iter):
                    self.queue.put(self._unpack(message._event.kv.value))
                self.cancel()
        except etcd3.exceptions.ConnectionFailedError as e:
            time.sleep(1)
            self._deliver(start_revision=start_revision)

    def _start(self):
        self.etcdclient = etcd3.client(
            host=self.host,
            port=self.port,
            grpc_options={
                "grpc.max_send_message_length": -1,
                "grpc.max_receive_message_length": -1,
            }.items(),
        )
        threading.Thread(target=self._deliver, daemon=True).start()

    def _stop(self):
        self.cancel()

    def _create(self):
        datadir = tempfile.mkdtemp()
        self._handle_exit(lambda: shutil.rmtree(datadir, ignore_errors=True))
        self._execute_command(
            "etcd --listen-client-urls=http://%s:%s --advertise-client-urls=http://%s:%s --data-dir=%s --listen-peer-urls=http://localhost:%s"
            % (
                self.host,
                self.port,
                self.host,
                self.port,
                datadir,
                port_for.select_random(),
            ),
            daemon=True,
        )
        self._execute_command(
            "etcdctl --endpoints=http://%s:%s endpoint status" % (self.host, self.port),
        )


class _BatchingBroadcast(module.Module):
    def __init__(self, batchsize=128):
        self.batch = [None] * batchsize
        self.nextpos = 0
        self.batchsize = batchsize
        self.deliverbatch = [None] * batchsize
        self.delivernextpos = batchsize
        self.queue = queue.Queue(maxsize=batchsize)
        self.stop_event = threading.Event()

    def broadcast(self, message):
        self.batch[self.nextpos] = message
        self.nextpos = self.nextpos + 1
        if self.nextpos == self.batchsize:
            self.southbound.broadcast(self.batch)
            self.nextpos = 0

    def deliver(self):
        try:
            return self.queue.get_nowait()
        except:
            raise Exception({"error": "no message to deliver"})

    def _deliver(self):
        while not self.stop_event.is_set():
            try:
                for message in self.southbound.deliver():
                    self.queue.put(message)
            except:
                pass

    def _start(self):
        threading.Thread(target=self._deliver, daemon=True).start()

    def _stop(self):
        self.stop_event.set()


class ETCD(module.Module):
    def __init__(self, host=None, port=None, queuesize=128, batchsize=128):
        self.port = port
        self.host = host
        self.queuesize = queuesize
        self.batchsize = batchsize
        if self.host == None:
            self.host = "localhost"
        if self.port == None:
            self.port = port_for.select_random()
        self.etcdbroadcast = _ETCDBroadcast(
            host=self.host, port=self.port, queuesize=self.queuesize
        )
        self.batchingbroadcast = _BatchingBroadcast(batchsize=self.batchsize)
        self.etcdbroadcast._register_northbound(self.batchingbroadcast)
        self.batchingbroadcast._register_southbound(self.etcdbroadcast)

    def broadcast(self, message):
        logger.info("broadcast: message=%s", message)
        return self.batchingbroadcast.broadcast(message)

    def deliver(self):
        message = self.batchingbroadcast.deliver()
        logger.info("deliver: message=%s" % (message,))
        return message

    def _create(self):
        logger.info("creating etcd at %s:%s" % (self.host, self.port))
        self.etcdbroadcast._create()
        self.batchingbroadcast._create()
        logger.info("finished creating etcd at %s:%s" % (self.host, self.port))

    def _uncreate(self):
        logger.info("uncreating etcd")
        self.batchingbroadcast._uncreate()
        self.etcdbroadcast._uncreate()

    def _start(self):
        logger.info("starting etcd at %s:%s" % (self.host, self.port))
        self.etcdbroadcast._start()
        self.batchingbroadcast._start()
        logger.info("finished starting etcd at %s:%s" % (self.host, self.port))

    def _stop(self):
        logger.info("stopping etcd")
        self.batchingbroadcast._stop()
        self.etcdbroadcast._stop()
