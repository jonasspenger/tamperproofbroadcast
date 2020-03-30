import unittest
import time


class TestMixin(unittest.TestCase):
    # total-order: both histories share same order of delivery
    # check: history of delivered messages of h1 is prefix of h2, or vice versa
    def total_order(self, test_time=60):
        # broadcast and deliver for test_time seconds
        t0 = time.time()
        i = 0
        while time.time() < t0 + test_time:
            for bc, hi in zip(self.broadcasts, self.histories):
                bc.broadcast(i)
                try:
                    for _ in range(2 ** 10):
                        hi.append(bc.deliver())
                except:
                    pass
            i = i + 1
            time.sleep(0.1)

        # check all histories longer than 0
        for hi in self.histories:
            self.assertTrue(len(hi) > 0)

        # check history from other pids longer than 0
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                self.assertTrue(len(pid_history) > 0)

        # check shortest history is equal to prefix of other histories
        for els in zip(*self.histories):
            e = els[0]
            for el in els:
                self.assertEqual(e, el)

    # fifo-order: messages of a process are delivered in the order they were broadcast by process
    # check: broadcast messages of h1 are delivered in same order in h2, and vice versa
    def fifo_order(self, test_time=60):
        # broadcast and deliver for test_time seconds
        t0 = time.time()
        i = 0
        while time.time() < t0 + test_time:
            for bc, hi in zip(self.broadcasts, self.histories):
                time.sleep(0.1)
                bc.broadcast(i)
                try:
                    for _ in range(2 ** 10):
                        hi.append(bc.deliver())
                except:
                    pass
            i = i + 1
            time.sleep(0.1)

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
                self.assertTrue(
                    all(seqnums[i] < seqnums[i + 1] for i in range(len(seqnums) - 1))
                )

    # no-creation: only messages that have been broadcast are delivered
    # check: if a message was delivered in h2 by p1, then it was previously broadcast in h1 by p1
    def no_creation(self, test_time=60):
        # broadcast and deliver for test_time seconds
        t0 = time.time()
        i = 0
        while time.time() < t0 + test_time:
            for bc, hi in zip(self.broadcasts, self.histories):
                bc.broadcast(i)
                try:
                    for _ in range(2 ** 10):
                        hi.append(bc.deliver())
                except:
                    pass
            i = i + 1
            time.sleep(0.1)

        # check all histories longer than 0
        for hi in self.histories:
            self.assertTrue(len(hi) > 0)

        # check history from other pids longer than 0
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                self.assertTrue(len(pid_history) > 0)

        # check each delivered message was previously broadcast
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                seqnums = [msg[2] for msg in pid_history]
                self.assertTrue(all(0 <= seqnums[j] <= i for j in range(len(seqnums))))

    def no_duplication(self, test_time=60):
        # broadcast and deliver for test_time seconds
        t0 = time.time()
        i = 0
        while time.time() < t0 + test_time:
            for bc, hi in zip(self.broadcasts, self.histories):
                bc.broadcast(i)
                try:
                    for _ in range(2 ** 10):
                        hi.append(bc.deliver())
                except:
                    pass
            i = i + 1
            time.sleep(0.1)

        # check all histories longer than 0
        for hi in self.histories:
            self.assertTrue(len(hi) > 0)

        # check history from other pids longer than 0
        for hi in self.histories:
            for bc in self.broadcasts:
                pid = bc.pid
                pid_history = [msg for msg in hi if msg[0] == pid]
                self.assertTrue(len(pid_history) > 0)

        # check no duplicate messages in history
        for hi in self.histories:
            self.assertTrue(len(hi) == len(set(hi)))
