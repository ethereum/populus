from populus.utils.formatting import remove_0x_prefix
from populus.utils.chains import get_chain_definition


def test_get_chain_definition(web3):
    block_0 = web3.eth.getBlock(0)
    chain_definition = get_chain_definition(web3)

    assert remove_0x_prefix(block_0['hash']) in chain_definition
    assert '0x' not in chain_definition

    _, _, anchor_block_hash = chain_definition.rpartition('/')
    anchor_block = web3.eth.getBlock(anchor_block_hash)
    assert anchor_block['hash'] == anchor_block_hash
