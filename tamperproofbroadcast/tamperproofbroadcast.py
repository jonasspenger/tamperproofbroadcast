import logging.config
import logging
import os
import module

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("tamperproofbroadcast")


class TamperProofBroadcast(module.Module):
    def broadcast(self, message):
        return self.southbound.broadcast(message)

    def deliver(self):
        return self.southbound.deliver()
