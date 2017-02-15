import os

from solc import (
    compile_files,
    get_solc_version,
)

from populus.utils.compile import (
    normalize_contract_data,
)
from populus.utils.linking import (
    link_bytecode_by_name,
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
        registrar_source_path = REGISTRAR_V3_SOURCE_PATH
    elif is_solc_04x():
        registrar_source_path = REGISTRAR_V4_SOURCE_PATH
    else:
        raise ValueError(
            "Unsupported version of solc.  Found: {0}.  Only 0.3.x and 0.4.x "
            "are supported".format(get_solc_version())
        )
    compiled_contracts = compile_files([registrar_source_path])
    raw_contract_data = compiled_contracts['Registrar']
    contract_data = normalize_contract_data(raw_contract_data)
    return contract_data


def get_registrar(web3, address=None):
    registrar_contract_data = get_compiled_registrar_contract()
    kwargs = dict(
        abi=registrar_contract_data['abi'],
        bytecode=registrar_contract_data['bytecode'],
        bytecode_runtime=registrar_contract_data['bytecode_runtime'],
    )
    if address is not None:
        kwargs['address'] = address
    return web3.eth.contract(**kwargs)


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

    expected_runtime = link_bytecode_by_name(
        contract_factory.bytecode_runtime,
        **link_dependencies
    )
    actual_runtime = web3.eth.getCode(contract_address)

    # If the runtime doesn't match then don't choose it.
    if actual_runtime != expected_runtime:
        return None

    return contract_factory(address=contract_address)
