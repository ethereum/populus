import pytest
import threading

from ethereum import tester

from populus.ethtester_client import EthTesterClient


def test_async_requests():
    client = EthTesterClient(async=True)

    threads = []
    errors = []
    to_addr = tester.encode_hex(tester.accounts[1])

    def spam_block_number():
        for i in range(5):
            try:
                client.send_transaction(
                    to=to_addr,
                    value=1,
                )
            except Exception as e:
                errors.append(e)
                pytest.fail(e.message)

    for i in range(5):
        thread = threading.Thread(target=spam_block_number)
        thread.daemon = True
        threads.append(thread)

    [thread.start() for thread in threads]

    [thread.join() for thread in threads]

    assert not errors
