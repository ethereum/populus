import pytest

from populus import Project


@pytest.mark.parametrize(
    'chain_name', ('temp', 'testrpc'),
)
def test_wait_for_block(project_dir, chain_name):
    project = Project()

    with project.get_chain(chain_name) as chain:
        web3 = chain.web3

        start_block = web3.eth.blockNumber
        chain.wait.for_block(start_block + 3, timeout=20)

        assert web3.eth.blockNumber >= start_block + 3


@pytest.mark.parametrize(
    'chain_name', ('temp', 'testrpc'),
)
def test_wait_for_receipt(project_dir, chain_name):
    project = Project()

    with project.get_chain(chain_name) as chain:
        if chain_name == 'temp':
            chain.wait.for_unlock()
        web3 = chain.web3

        txn_hash = web3.eth.sendTransaction({
            'to': web3.eth.coinbase,
            'value': 1234,
        })
        txn_receipt = chain.wait.for_receipt(txn_hash)
        assert txn_receipt['transactionHash'] == txn_hash


@pytest.mark.parametrize(
    'chain_name', ('temp', 'testrpc'),
)
def test_wait_for_contract_address(project_dir, chain_name, MATH_CODE, MATH_RUNTIME):
    project = Project()

    with project.get_chain(chain_name) as chain:
        if chain_name == 'temp':
            chain.wait.for_unlock()
        web3 = chain.web3

        txn_hash = web3.eth.sendTransaction({
            'data': MATH_CODE,
            'gas': 2000000,
        })
        contract_address = chain.wait.for_contract_address(txn_hash)

        chain_code = web3.eth.getCode(contract_address)
        assert chain_code == MATH_RUNTIME
