from populus.utils.hexadecimal import hexbytes_to_hexstr


def test_getting_contract_data(chain, math):
    provider = chain.provider

    contract_data = provider.get_contract_data('Math')
    assert hexbytes_to_hexstr(math.bytecode) == contract_data['bytecode']
