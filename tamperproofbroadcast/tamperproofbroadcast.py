import logging.config
import threading
import argparse
import logging
import inspect
import sys
import os
import multichain
import protocols
import module
import etcd
import time

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("tamperproofbroadcast")


class TamperProofBroadcast(module.Module):
    @classmethod
    def _Parser(cls):
        parser = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers(dest="protocol", required=True)
        fotb = subparsers.add_parser(
            "fotb",
            help="FIFO-order reliable tamper-proof broadcast",
            description="FIFO-order reliable tamper-proof broadcast",
            parents=[protocols.FOTB._Parser(), multichain.MultiChain._Parser(),],
        )
        totb = subparsers.add_parser(
            "totb",
            help="uniform causal-order total-order reliable tamper-proof broadcast",
            description="uniform causal-order total-order reliable tamper-proof broadcast",
            parents=[protocols.TOTB._Parser(), multichain.MultiChain._Parser(),],
        )
        htlltb = subparsers.add_parser(
            "htlltb",
            help="high throughput low latency uniform total-order (causal-order) reliable tamper-proof broadcast",
            description="high throughput low latency uniform total-order (causal-order) reliable tamper-proof broadcast",
            parents=[
                protocols.HTLLTB._Parser(),
                protocols.FOTB._Parser(),
                multichain.MultiChain._Parser(),
                etcd.ETCD._Parser(),
            ],
        )
        htlltbtest = subparsers.add_parser(
            "htlltbtest", parents=[protocols.HTLLTBTEST._Parser(), etcd.ETCD._Parser()],
        )
        return parser

    @classmethod
    def _Init(cls, args):
        protocol = args.protocol
        if protocol == "fotb":
            fotb = protocols.FOTB._Init(args)
            mc = multichain.MultiChain._Init(args)
            mc._register_northbound(fotb)
            fotb._register_southbound(mc)
            return fotb
        if protocol == "totb":
            totb = protocols.TOTB._Init(args)
            mc = multichain.MultiChain._Init(args)
            mc._register_northbound(totb)
            totb._register_southbound(mc)
            return totb
        if protocol == "htlltb":
            htlltb = protocols.HTLLTB._Init(args)
            fotb = protocols.FOTB._Init(args)
            mc = multichain.MultiChain._Init(args)
            et = etcd.ETCD._Init(args)
            mc._register_northbound(fotb)
            fotb._register_southbound(mc)
            fotb._register_northbound(htlltb)
            htlltb._register_southbound(fotb, name="fotb")
            htlltb._register_southbound(et, name="etcd")
            return htlltb
        if protocol == "htlltbtest":
            htlltbtest = protocols.HTLLTBTEST._Init(args)
            et = etcd.ETCD._Init(args)
            htlltbtest._register_southbound(et, name="etcd")
            return htlltbtest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[TamperProofBroadcast._Parser(),])
    parser.add_argument("--logginglevel", default="INFO")
    args = parser.parse_args()
    logging.getLogger().setLevel(args.logginglevel)
    tpb = TamperProofBroadcast._Init(args)
    tpb._create()
    tpb._start()

    def receive():
        while True:
            print(tpb.deliver(blocking=True))

    threading.Thread(target=receive, daemon=True).start()
    while True:
        tpb.broadcast(sys.stdin.readline())

    tpb._stop()
    tpb._uncreate()
