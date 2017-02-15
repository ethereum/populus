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
    '__'  # Prefixed by double underscore
    '[a-zA-Z_]'  # First letter must be alpha or underscore
    '[a-zA-Z0-9_]{0,59}?'  # Intermediate letters
    '_{0,59}'
    '__'  # End with a double underscore
)


LinkReference = collections.namedtuple(
    'LinkReference',
    ['reference_name', 'full_name', 'offset', 'length'],
)


def remove_dunderscore_wrapper(value):
    return remove_dunderscore_prefix(value.rstrip('_'))


@to_tuple
@coerce_args_to_text
def find_link_references(bytecode, full_reference_names):
    """
    Given bytecode, this will return all of the linked references from within
    the bytecode.
    """
    unprefixed_bytecode = remove_0x_prefix(bytecode)

    expand_fn = functools.partial(
        expand_shortened_reference_name,
        full_reference_names=full_reference_names,
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


def expand_shortened_reference_name(short_name, full_reference_names):
    """
    Link references whos names are longer than their bytecode representations
    will get truncated to 4 characters short of their full name because of the
    double underscore prefix and suffix.

    This expands `short_name` to it's full name or raise a value error if it is
    unable to find an appropriate expansion.
    """
    if short_name in full_reference_names:
        return short_name

    candidates = [
        full_name for full_name in full_reference_names if full_name.startswith(short_name)
    ]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        raise ValueError(
            "Multiple candidates found trying to expand '{0}'.  Found '{1}'. "
            "Searched '{2}'".format(
                short_name,
                ','.join(candidates),
                ','.join(full_reference_names),
            )
        )
    else:
        raise ValueError(
            "Unable to expand '{0}'. "
            "Searched '{1}'".format(
                short_name,
                ','.join(full_reference_names),
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
    unresolved_link_references = find_link_references(bytecode, link_names_and_values.keys())
    link_reference_values = [
        (link_reference, link_names_and_values[link_reference.full_name])
        for link_reference in unresolved_link_references
    ]
    linked_bytecode = link_bytecode(bytecode, link_reference_values)
    return linked_bytecode
