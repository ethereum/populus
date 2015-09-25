from ethereum import tester as t


class EthTesterClient(object):
    """
    Stand-in replacement for the rpc client.
    """
    def send_transaction(self, *args, **kwargs):
        assert False
