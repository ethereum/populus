from ethereum.tester import ABIContract
from ethereum import utils as ethereum_utils


class ContractBase(object):
    def __init__(self, address):
        self.address = address


def get_abi_signature(func_name, inputs):
    signature = "{func_name}({arg_types})".format(
        func_name=func_name,
        arg_types=','.join(inputs),
    )
    return ethereum_utils.big_endian_to_int(ethereum_utils.sha3(signature)[:4])


def get_docstring_signature(func_name, inputs):
    """
    TODO: deal with returns
    """
    signature = "{func_name}({input_args})".format(
        func_name=func_name,
        input_args=','.join(
            "{type} {arg_name}".format(type=i['type'], arg_name=i['name'])
            for i in inputs
        ),
    )
    return signature


class Function(object):
    def __init__(self, name, inputs):
        assert False

    def __call__(self, *args):
        assert False


class Event(object):
    def __init__(self, name, inputs):
        assert False

    def __call__(self, *args):
        assert False


def Contract(client, contract_name, contract):
    abi = contract['info']['abiDefinition']
    _dict = {
        'client': client,
        'code': contract['code'],
        'abi': abi,
    }

    functions = []
    events = []

    for signature_item in abi:
        if signature_item['type'] == 'constructor':
            # Constructors don't need to be part of a contract's methods
            continue

        if signature_item['name'] in _dict:
            raise ValueError("About to overwrite a function signature for duplicate function name {0}".format(signature_item['name']))

        if signature_item['type'] == 'function':
            # make sure we're not overwriting a signature

            func = Function(**signature_item)
            _dict[signature_item['name']] = func
            functions.append(func)
        elif signature_item['type'] == 'event':
            event = Event(**signature_item)
            _dict[signature_item['name']] = event
            events.append(event)
        else:
            raise ValueError("Unknown signature item '{0}'".format(signature_item))

    docstring = """
    contract {contract_name} {
    // Events
    {events}

    // Functions
    {functions}
    }
    """.format(
        contract_name=contract_name,
        functions='\n'.join(str(f) for f in functions),
        events='\n'.join(str(e) for e in events),
    )

    _dict['__doc__'] = docstring

    return type(contract_name, (object,), _dict)
