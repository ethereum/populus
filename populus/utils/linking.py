import json
import re
import functools
import collections

from eth_utils import (
    coerce_args_to_text,
    remove_0x_prefix,
    add_0x_prefix,
    to_tuple,
    compose,
)

from .formatting import (
    remove_dunderscore_prefix,
)


DEPENDENCY_RE = (
    r'__'  # Prefixed by double underscore
    r'.{36}'  # 36 characters of dubious character
    r'__'  # End with a double underscore
)


LinkReference = collections.namedtuple(
    'LinkReference',
    ['reference_name', 'full_name', 'offset', 'length'],
)


def remove_dunderscore_wrapper(value):
    return remove_dunderscore_prefix(value.rstrip('_'))


@to_tuple
@coerce_args_to_text
def find_link_references(bytecode, reference_keys):
    """
    Given bytecode, this will return all of the linked references from within
    the bytecode.
    """
    unprefixed_bytecode = remove_0x_prefix(bytecode)

    expand_fn = functools.partial(
        expand_shortened_reference_name,
        reference_keys=reference_keys,
    )

    link_references = tuple((
        LinkReference(
            reference_name=remove_dunderscore_wrapper(match.group()),
            full_name=expand_fn(remove_dunderscore_wrapper(match.group())),
            offset=match.start(),
            length=match.end() - match.start(),
        ) for match in re.finditer(DEPENDENCY_RE, unprefixed_bytecode)
    ))

    return link_references


def expand_shortened_reference_name(short_key, reference_keys):
    """
    Link references whos names are longer than their bytecode representations
    will get truncated to 4 characters short of their full name because of the
    double underscore prefix and suffix.

    This expands `short_key` to it's full name or raise a value error if it is
    unable to find an appropriate expansion.
    """
    short_path, sep, short_name = short_key.rpartition(':')

    use_primitive = True
    processed_reference_keys = []
    for k in reference_keys:
        if isinstance(k, tuple):
            use_primitive = False
        else:
            path, _, sym = k.rpartition(':')
            k = (path, sym)
        processed_reference_keys.append(k)

    if (short_path, short_name) in processed_reference_keys:
        if use_primitive:
            return short_key
        else:
            return (short_path, short_name)

    candidates = [
        (full_path, full_name) for full_path, full_name in processed_reference_keys
        if (full_path+':'+full_name).startswith(short_key) or
           full_name.startswith(short_key) or
           not full_path and full_name.startswith(short_name)
    ]
    if len(candidates) == 1:
        if use_primitive:
            path, sym = candidates[0]
            if path:
                return path+':'+sym
            return sym
        else:
            return candidates[0]
    elif len(candidates) > 1:
        raise ValueError(
            "Multiple candidates found trying to expand '{0}'.  Found '{1}'. "
            "Searched '{2}'".format(
                short_key,
                candidates,
                processed_reference_keys,
            )
        )
    else:
        raise ValueError(
            "Unable to expand '{0}'. "
            "Searched {1}".format(
                short_key,
                json.dumps(list(processed_reference_keys), indent=2),
            )
        )


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
    """
    linker_fn = compose(*(
        functools.partial(
            insert_link_value,
            value=value,
            offset=link_reference.offset,
        )
        for link_reference, value in link_reference_values
    ))
    linked_bytecode = linker_fn(bytecode)
    return linked_bytecode


def link_bytecode_by_name(bytecode, **link_names_and_values):
    """
    Helper function for linking bytecode with a mapping of link reference names
    to their values.
    """
    processed_link_names_and_values = {}
    for rawkey, value in link_names_and_values.items():
        path, _, sym = rawkey.rpartition(':')
        processed_link_names_and_values[(path, sym)] = value

    unresolved_link_references = find_link_references(bytecode, processed_link_names_and_values.keys())
    link_reference_values = [
        (link_reference, processed_link_names_and_values[link_reference.full_name])
        for link_reference in unresolved_link_references
    ]
    linked_bytecode = link_bytecode(bytecode, link_reference_values)
    return linked_bytecode
