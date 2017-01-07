from populus.utils.packaging import get_chain_definition

def test_get_chain_definition(web3):
    chain_definition = get_chain_definition(web3)
    assert chain_definition == 'blockchain://0x040db90fe13e6688c86ff93c5ce8e4a0a61faaf6a734c548febd0d0b44c86aa8/block/212a8d39e6a76e3f40dd2ad7d4fd61f07cd896c946e4d76160b5c6bcd922cd78'
