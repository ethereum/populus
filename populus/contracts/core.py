import copy
import hashlib
import collections
import itertools

from ethereum import utils as ethereum_utils

from populus.contracts.functions import (
    Function,
    FunctionGroup,
)
from populus.contracts.events import Event


class ContractBase(object):
    def __init__(self, address, blockchain_client):
        functions = {fn.name: fn for fn in (copy.copy(f) for f in self._config._functions)}
        events = {ev.name: ev for ev in (copy.copy(e) for e in self._config._events)}
        for obj in itertools.chain(functions.values(), events.values()):
            obj._bind(self)
        self._meta = ContractMeta(address, blockchain_client, functions, events)

    def __str__(self):
        return "{name}({address})".format(name=self.__class__.__name__, address=self.address)

    @classmethod
    def get_deploy_data(cls, *args):
        data = cls._config.code
        if args:
            if cls._config.constructor is None:
                raise ValueError("This contract does not appear to have a constructor")
            data += ethereum_utils.encode_hex(cls._config.constructor.abi_args_signature(args))

        return data

    #
    #  Instance Methods
    #
    def get_balance(self, block="latest"):
        return self._meta.blockchain_client.get_balance(self._meta.address, block=block)


class ContractMeta(object):
    """
    Instance level contract data.
    """
    def __init__(self, address, blockchain_client, functions, events):
        self.address = address
        self.blockchain_client = blockchain_client
        self.functions = functions
        self.events = events


class Config(object):
    """
    Contract (class) level contract data.
    """
    def __init__(self, code, source, abi, functions, events, constructor,
                 contract_name=None):
        self.code = code
        self.source = source
        self.abi = abi
        self._functions = functions
        self._events = events
        self.constructor = constructor
        self.name = contract_name


def Contract(contract_meta, contract_name=None):
    _abi = contract_meta['info']['abiDefinition']
    code = contract_meta['code']
    source = contract_meta['info']['source']

    if contract_name is None:
        contract_name = "Unknown-{0}".format(hashlib.md5(code).hexdigest())

    functions = []
    events = []
    constructor = None

    _dict = {}
    _functions = collections.defaultdict(list)

    for signature_item in _abi:
        if signature_item['type'] == 'constructor':
            # Constructors don't need to be part of a contract's methods
            if signature_item.get('inputs'):
                constructor = Function(
                    name='constructor',
                    inputs=signature_item['inputs'],
                )
            continue

        if signature_item['type'] == 'function':
            # make sure we're not overwriting a signature

            func = Function(
                name=signature_item['name'],
                inputs=signature_item['inputs'],
                outputs=signature_item['outputs'],
                constant=signature_item['constant'],
            )
            _functions[signature_item['name']].append(func)
        elif signature_item['type'] == 'event':
            if signature_item['name'] in _dict:
                # TODO: handle namespace conflicts
                raise ValueError("About to overwrite a function signature for duplicate function name {0}".format(signature_item['name']))  # NOQA
            event = Event(
                name=signature_item['name'],
                inputs=signature_item['inputs'],
                anonymous=signature_item['anonymous'],
            )
            _dict[signature_item['name']] = event
            events.append(event)
        else:
            raise ValueError("Unknown signature item '{0}'".format(signature_item))

    # Now process all the functions
    for fn_name, fn_list in _functions.items():
        if len(fn_list) == 1:
            _dict[fn_name] = fn_list[0]
            functions.append(fn_list[0])
        else:
            fn_group = FunctionGroup(fn_list)
            _dict[fn_name] = fn_group
            functions.append(fn_group)

    docstring = """
    contract {contract_name} {{
    // Events
    {events}

    // Functions
    {functions}
    }}
    """.format(
        contract_name=contract_name,
        functions='\n'.join(str(f) for f in functions),
        events='\n'.join(str(e) for e in events),
    )

    _dict['__doc__'] = docstring
    _dict['_config'] = Config(
        code, source, _abi, functions, events, constructor, contract_name,
    )

    return type(str(contract_name), (ContractBase,), _dict)


def package_contracts(contracts):
    contract_classes = {
        name: Contract(contract_meta, name) for name, contract_meta in contracts.items()
    }

    _dict = {
        '__len__': lambda s: len(contract_classes),
        '__iter__': lambda s: iter(contract_classes.items()),
        '__getitem__': lambda s, k: contract_classes.__getitem__[k],
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()
