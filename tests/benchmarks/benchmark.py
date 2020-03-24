import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../tamperproofbroadcast"))

from google.cloud import storage
import logging
import time
import tamperproofbroadcast
import module


class Benchmark(module.Module):
    def __init__(self, duration=5, testid="test-1", bucketname=None):
        self.duration = int(duration)
        self.testid = testid
        self.bucketname = bucketname

    def _start(self):
        logging.info("starting benchmark")
        t0 = time.time()
        messagenumber = 0
        deliverednumber = 0
        fname = self.testid + ".log"
        f = open(fname, "w")
        f.write("operation processid messagenumber time\n")
        logt = int(time.time())
        while time.time() < t0 + self.duration:
            if int(time.time()) > logt + 5:
                logt = int(time.time())
                logging.info(
                    "%s broadcast messages and %s delivered messages after %s seconds"
                    % (messagenumber, deliverednumber, int(time.time() - t0))
                )
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
                for _ in range(2056):
                    message = self.southbound.deliver()[2]
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
                    deliverednumber = deliverednumber + 1
            except Exception as e:
                f.write(str(e) + "\n")
        f.close()
        logging.info(
            "%s broadcast messages and %s delivered messages after %s seconds"
            % (messagenumber, deliverednumber, int(time.time() - t0))
        )
        logging.info("benchmark finished")
        if self.bucketname is not None:
            logging.info("uploading file to google cloud storage")
            client = storage.Client()
            bucket = client.get_bucket(self.bucketname)
            blob = bucket.blob(fname)
            blob.upload_from_filename(fname)
            logging.getLogger.info("upload finished")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        parents=[
            Benchmark._Parser(),
            tamperproofbroadcast.TamperProofBroadcast._Parser(),
        ]
    )
    parser.add_argument("--logginglevel", default="INFO")
    args = parser.parse_args()
    logging.getLogger().setLevel(args.logginglevel)

    tpb = tamperproofbroadcast.TamperProofBroadcast._Init(args)
    bench = Benchmark._Init(args)
    tpb._register_northbound(bench)
    bench._register_southbound(tpb)
    tpb._create()
    bench._create()
    tpb._start()
    bench._start()
    bench._stop()
    tpb._stop()
    bench._uncreate()
    tpb._uncreate()
