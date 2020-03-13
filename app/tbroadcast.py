import module

class TBroadcast(module.Module):
    def __init__(self, pid=None):
        self.pid = pid

    def broadcast(self, messages):
        return self.southbound.broadcast((self.pid, messages))

    def deliver(self, lsn):
        return self.southbound.deliver(lsn)

    def info(self):
        return "pid: %s" % (self.pid)
