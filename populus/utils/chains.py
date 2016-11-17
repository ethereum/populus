import os
import re

from web3 import (
    Web3,
    RPCProvider,
    IPCProvider,
    HTTPProvider,
    TestRPCProvider,
)

from .formatting import (
    add_0x_prefix,
    remove_0x_prefix,
)
from .six import (
    parse,
)
from .types import (
    is_integer,
)
from .module_loading import (
    import_string,
)


BASE_BLOCKCHAIN_STORAGE_DIR = "./chains"


def get_base_blockchain_storage_dir(project_dir):
    base_blochcain_storage_dir = os.path.join(project_dir, BASE_BLOCKCHAIN_STORAGE_DIR)
    return base_blochcain_storage_dir


def setup_web3_from_config(web3_config):
    ProviderClass = import_string(web3_config['provider.class'])

    provider_kwargs = {}

    if issubclass(ProviderClass, (RPCProvider, TestRPCProvider)):
        if 'provider.settings.rpc_host' in web3_config:
            provider_kwargs['host'] = web3_config['provider.settings.rpc_host']

        if 'provider.settings.rpc_port' in web3_config:
            provider_kwargs['port'] = web3_config['provider.settings.rpc_port']

        if 'provider.settings.use_ssl' in web3_config:
            provider_kwargs['ssl'] = web3_config['provider.settings.use_ssl']
    elif issubclass(ProviderClass, IPCProvider):
        if 'provider.settings.ipc_path' in web3_config:
            provider_kwargs['ipc_path'] = web3_config['provider.settings.ipc_path']
    elif issubclass(ProviderClass, HTTPProvider):
        if 'provider.settings.endpoint_uri' in web3_config:
            provider_kwargs['endpoint_uri'] = web3_config['provider.settings.endpoint_uri']

    web3 = Web3(ProviderClass(**provider_kwargs))

    if 'eth.default_account' in web3_config:
        web3.eth.defaultAccount = web3_config['eth.default_account']

    return web3


def setup_chain_from_config(project, chain_name, chain_config):
    chain_class_import_path = chain_config['chain.class']

    ChainClass = import_string(chain_class_import_path)
    chain = ChainClass(project, chain_name, chain_config)
    return chain


BLOCK_OR_TRANSACTION_HASH_REGEX = "^(?:0x)?[a-zA-Z0-9]{64}$"


def is_block_or_transaction_hash(value):
    return bool(re.match(BLOCK_OR_TRANSACTION_HASH_REGEX, value))


BLOCK = 'block'
TRANSACTION = 'transaction'


def create_BIP122_uri(chain_id, resource_type, resource_identifier):
    """
    See: https://github.com/bitcoin/bips/blob/master/bip-0122.mediawiki
    """
    if resource_type not in {BLOCK, TRANSACTION}:
        raise ValueError("Invalid resource_type.  Must be one of 'block' or 'transaction'")
    elif not is_block_or_transaction_hash(resource_identifier):
        raise ValueError("Invalid resource_identifier.  Must be a hex encoded 32 byte value")
    elif not is_block_or_transaction_hash(chain_id):
        raise ValueError("Invalid chain_id.  Must be a hex encoded 32 byte value")

    return parse.urlunsplit([
        'blockchain',
        remove_0x_prefix(chain_id),
        "{0}/{1}".format(resource_type, remove_0x_prefix(resource_identifier)),
        '',
        '',
    ])


def create_block_uri(chain_id, block_identifier):
    if is_integer(block_identifier):
        return create_BIP122_uri(chain_id, 'block', str(block_identifier))
    else:
        return create_BIP122_uri(chain_id, 'block', remove_0x_prefix(block_identifier))


def create_transaction_uri(chain_id, transaction_hash):
    return create_BIP122_uri(chain_id, 'transaction', transaction_hash)


def get_chain_id(web3):
    return web3.eth.getBlock(0)['hash']


def get_chain_definition(web3, min_block_number=0, num_confirmations=0):
    """
    Return the blockchain URI that
    """
    chain_id = get_chain_id(web3)
    latest_block = web3.eth.getBlock('latest')
    latest_block_number = latest_block['number']

    target_block_number = latest_block_number - num_confirmations
    if target_block_number < min_block_number:
        raise ValueError("Cannot generate chain definition matching given constraints")

    block_for_definition = web3.eth.getBlock(target_block_number)
    block_hash_for_definition = block_for_definition['hash']

    return create_block_uri(chain_id, block_hash_for_definition)


BIP122_URL_REGEX = (
    "^"
    "blockchain://"
    "(?P<chain_id>[a-zA-Z0-9]{64})"
    "/"
    "(?P<resource_type>block|transaction)"
    "/"
    "(?P<resource_hash>[a-zA-Z0-9]{64})"
    "$"
)


def is_BIP122_uri(value):
    return bool(re.match(BIP122_URL_REGEX, value))


def parse_BIP122_uri(blockchain_uri):
    match = re.match(BIP122_URL_REGEX, blockchain_uri)
    if match is None:
        raise ValueError("Invalid URI format: '{0}'".format(blockchain_uri))
    chain_id, resource_type, resource_hash = match.groups()
    return (
        add_0x_prefix(chain_id),
        resource_type,
        add_0x_prefix(resource_hash),
    )


def is_BIP122_block_uri(value):
    if not is_BIP122_uri(value):
        return False
    _, resource_type, _ = parse_BIP122_uri(value)
    return resource_type == BLOCK


def is_BIP122_transaction_uri(value):
    if not is_BIP122_uri(value):
        return False
    _, resource_type, _ = parse_BIP122_uri(value)
    return resource_type == TRANSACTION


def check_if_chain_matches_chain_uri(web3, blockchain_uri):
    chain_id, resource_type, resource_hash = parse_BIP122_uri(blockchain_uri)
    genesis_block = web3.eth.getBlock('earliest')
    if genesis_block['hash'] != chain_id:
        return False

    if resource_type == BLOCK:
        resource = web3.eth.getBlock(resource_hash)
    elif resource_type == TRANSACTION:
        resource = web3.eth.getTransaction(resource_hash)
    else:
        raise ValueError("Unsupported resource type: {0}".format(resource_type))

    if resource['hash'] == resource_hash:
        return True
    else:
        return False
