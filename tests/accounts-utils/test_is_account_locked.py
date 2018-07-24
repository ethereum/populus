import pytest

from eth_utils import (
    to_text,
)

from geth.accounts import create_new_account

from populus.utils.accounts import (
    is_account_locked,
)


@pytest.mark.skip(reason="This is currently broken in latest geth")
def test_with_locked_account(project):
    temp_chain = project.get_chain('temp')

    account = to_text(
        create_new_account(temp_chain.geth.data_dir, b'a-test-password')
    )

    with temp_chain:
        web3 = temp_chain.web3

        assert account in web3.eth.accounts
        assert is_account_locked(web3, account) is True

        assert web3.personal.unlockAccount(account, 'a-test-password')

        assert is_account_locked(web3, account) is False
