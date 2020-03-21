import sys

sys.path.append("tamperproofbroadcast")

from google.cloud import storage
import time
import os
import tamperproofbroadcast
import etcdbroadcast
import batchingbroadcast
import module


class Benchmark(module.Module):
    def __init__(self, duration=5, testid="test-1"):
        self.duration = int(duration)
        self.testid = testid

    def _start(self):
        t0 = time.time()
        messagenumber = 0
        fname = self.testid + ".log"
        f = open(fname, "w")
        f.write("operation processid messagenumber time\n")
        while time.time() < t0 + self.duration:
            try:
                message = (self.testid, messagenumber, os.urandom(256))
                self.southbound.broadcast(message)
                messagenumber = messagenumber + 1
                logmessage = (
                    "broadcast"
                    + " "
                    + str(message[0])
                    + " "
                    + str(message[1])
                    + " "
                    + str(time.time())
                    + "\n"
                )
                f.write(logmessage)
            except Exception as e:
                f.write(str(e))
            try:
                for _ in range(128):
                    message = self.southbound.deliver()
                    logmessage = (
                        "deliver"
                        + " "
                        + str(message[0])
                        + " "
                        + str(message[1])
                        + " "
                        + str(time.time())
                        + "\n"
                    )
                    f.write(logmessage)
            except Exception as e:
                f.write(str(e) + "\n")
        f.close()
        client = storage.Client()
        bucket = client.get_bucket("tpbexperiment")
        blob = bucket.blob(fname)
        blob.upload_from_filename(fname)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        parents=[
            Benchmark._Parser(),
            tamperproofbroadcast.TamperProofBroadcast._Parser(),
            batchingbroadcast.BatchingBroadcast._Parser(),
            etcdbroadcast.ETCDBroadcast._Parser(),
        ]
    )
    args = parser.parse_args()

    etcdbc = etcdbroadcast.ETCDBroadcast._Init(args)
    bb = batchingbroadcast.BatchingBroadcast._Init(args)
    tpbc = tamperproofbroadcast.TamperProofBroadcast._Init(args)
    b = Benchmark._Init(args)

    etcdbc._register_northbound(bb)
    bb._register_northbound(tpbc)
    tpbc._register_northbound(b)

    b._register_southbound(tpbc)
    tpbc._register_southbound(bb)
    bb._register_southbound(etcdbc)

    etcdbc._create()
    bb._create()
    tpbc._create()
    b._create()

    etcdbc._start()
    bb._start()
    tpbc._start()
    b._start()

    b._stop()
    tpbc._stop()
    bb._stop()
    etcdbc._stop()
