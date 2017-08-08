import re
import functools

from cytoolz.functoolz import (
    compose,
)

from eth_utils import (
    coerce_args_to_text,
    remove_0x_prefix,
    add_0x_prefix,
    to_tuple,
)

from .formatting import (
    remove_dunderscore_prefix,
)


DEPENDENCY_RE = (
    r'__'  # Prefixed by double underscore
    r'.{36}'  # 36 characters of dubious character
    r'__'  # End with a double underscore
)


# start and length should be `byte` offsets meaning they represent the
# start/length in the bytecode in its bytes representation.  To transate to hex
# representation, these two numbers should be multiplied by two.
def LinkReference(source_path, name, start, length):
    return {
        'source_path': source_path,
        'name': name,
        'start': start,
        'length': length,
    }


#
# Standard JSON utils
#
@to_tuple
def normalize_standard_json_link_references(link_references):
    for source_path, names in link_references.items():
        for contract_name, reference_locations in names.items():
            for location in reference_locations:
                yield LinkReference(
                    source_path=source_path,
                    name=contract_name,
                    start=location['start'] * 2,  # convert binary offsets to hex
                    length=location['length'] * 2,  # convert binary offsets to hex
                )


#
# Combined JSON utils
#
def remove_dunderscore_wrapper(value):
    return remove_dunderscore_prefix(value.rstrip('_'))


@to_tuple
@coerce_args_to_text
def find_placeholder_locations(bytecode):
    """
    Given bytecode, this will return all of the linked references from within
    the bytecode.
    """
    unprefixed_bytecode = remove_0x_prefix(bytecode)

    for match in re.finditer(DEPENDENCY_RE, unprefixed_bytecode):
        start = match.start()
        length = match.end() - start
        placeholder = unprefixed_bytecode[start:start + length]
        yield (remove_dunderscore_wrapper(placeholder), start, length)


def expand_placeholder(placeholder, full_names):
    """
    Link references whos names are longer than their bytecode representations
    will get truncated to 4 characters short of their full name because of the
    double underscore prefix and suffix.  This embedded string is referred to
    as the `placeholder`

    This expands `placeholder` to it's full reference name or raise a value
    error if it is unable to find an appropriate expansion.
    """
    if placeholder in full_names:
        return placeholder

    candidates = [
        full_name
        for full_name
        in full_names
        if full_name.startswith(placeholder)
    ]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        raise ValueError(
            "Multiple candidates found trying to expand '{0}'.  Found '{1}'. "
            "Searched '{2}'".format(
                placeholder,
                ", ".join(candidates),
                ", ".join(full_names),
            )
        )
    else:
        raise ValueError(
            "Unable to expand '{0}'. "
            "Searched {1}".format(
                placeholder,
                ", ".join(full_names),
            )
        )


@to_tuple
def normalize_placeholder_link_references(placeholder_locations, compiled_contracts):
    all_contract_names = set(
        contract_data['name']
        for contract_data
        in compiled_contracts
    )
    contract_source_paths = {
        contract_data['name']: contract_data['source_path']
        for contract_data
        in compiled_contracts
    }

    for placeholder, start, length in placeholder_locations:
        contract_name = expand_placeholder(placeholder, all_contract_names)
        source_path = contract_source_paths[contract_name]
        yield LinkReference(
            source_path=source_path,
            name=contract_name,
            start=start,
            length=length,
        )


#
# Bytecode Linking utils
#
def insert_link_value(bytecode, value, offset):
    return add_0x_prefix(''.join((
        remove_0x_prefix(bytecode)[:offset],
        remove_0x_prefix(value),
        remove_0x_prefix(bytecode)[offset + len(remove_0x_prefix(value)):]
    )))


def link_bytecode(bytecode, link_reference_values):
    """
    Given the bytecode for a contract, and it's dependencies in the form of
    {contract_name: address} this functino returns the bytecode with all of the
    link references replaced with the dependency addresses.

    TODO: validate that the provided values are of the appropriate length
    """
    linker_fn = compose(*(
        functools.partial(
            insert_link_value,
            value=value,
            offset=link_reference['start'],
        )
        for link_reference, value in link_reference_values
    ))
    linked_bytecode = linker_fn(bytecode)
    return linked_bytecode
