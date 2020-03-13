import logging.config
import multichaincli
import logging
import module

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))
logger = logging.getLogger("blockchain")


class Multichain(multichaincli.Multichain, module.Module):
    """Create, start, and communicate (RPC) with multichain blockchain server.

    Blockchain RPC abstraction of the multichain blockchain.
    """

    def __init__(
        self,
        rpcuser="user",
        rpcpasswd="password",
        rpcport=7208,
        rpchost="localhost",
        chainname="chain",
    ):
        self.rpcuser = rpcuser
        self.rpcpasswd = rpcpasswd
        self.rpcport = rpcport
        self.rpchost = rpchost
        self.chainname = chainname
        super().__init__(
            self.rpcuser,
            self.rpcpasswd,
            self.rpchost,
            self.rpcport,
            self.chainname.split("@")[0],
        )
        self._handle_exit(sys.exit)
