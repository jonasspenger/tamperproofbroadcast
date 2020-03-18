import logging.config
import threading
import logging
import queue
import os
import module

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("batchingbroadcast")


class BatchingBroadcast(module.Module):
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
