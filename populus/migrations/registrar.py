import os

from solc import (
    compile_files,
    get_solc_version,
)

from populus.utils.contracts import (
    link_bytecode,
)


def is_solc_03x():
    version = get_solc_version()
    major, minor, _ = version.split('.')[:3]
    return major == '0' and minor == '3'


def is_solc_04x():
    version = get_solc_version()
    major, minor, _ = version.split('.')[:3]
    return major == '0' and minor == '4'


BASE_DIR = os.path.dirname(__file__)


REGISTRAR_V3_SOURCE_PATH = os.path.join(BASE_DIR, 'RegistrarV3.sol')
REGISTRAR_V4_SOURCE_PATH = os.path.join(BASE_DIR, 'RegistrarV4.sol')


def get_compiled_registrar_contract():
    if is_solc_03x():
        compiled_contracts = compile_files([REGISTRAR_V3_SOURCE_PATH])
    elif is_solc_04x():
        compiled_contracts = compile_files([REGISTRAR_V4_SOURCE_PATH])
    else:
        raise ValueError(
            "Unsupported version of solc.  Found: {0}.  Only 0.3.x and 0.4.x "
            "are supported".format(get_solc_version())
        )
    contract_data = compiled_contracts['Registrar']
    return contract_data


def get_registrar(web3, address=None):
    registrar_contract_data = get_compiled_registrar_contract()
    return web3.eth.contract(
        address=address,
        abi=registrar_contract_data['abi'],
        code=registrar_contract_data['code'],
        code_runtime=registrar_contract_data['code_runtime'],
    )


def get_contract_from_registrar(chain,
                                contract_name,
                                contract_factory,
                                link_dependencies=None):
    if link_dependencies is None:
        link_dependencies = {}

    web3 = chain.web3
    registrar = chain.registrar
    registrar_key = 'contract/{name}'.format(name=contract_name)

    if not registrar.call().exists(registrar_key):
        return None

    contract_address = registrar.call().getAddress(registrar_key)

    expected_runtime = link_bytecode(
        contract_factory.code_runtime,
        **link_dependencies
    )
    actual_runtime = web3.eth.getCode(contract_address)

    # If the runtime doesn't match then don't choose it.
    if actual_runtime != expected_runtime:
        return None

    return contract_factory(address=contract_address)
