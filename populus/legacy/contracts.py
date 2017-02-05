from populus.utils.linking import (
    find_link_references,
)


def get_contract_library_dependencies(bytecode, full_contract_names):
    """
    Given a contract bytecode and an iterable of all of the known full names of
    contracts, returns a set of the contract names that this contract bytecode
    depends on.
    To get the full dependency graph use the `get_recursive_contract_dependencies`
    function.
    """
    return {
        ref.full_name for ref in find_link_references(bytecode, full_contract_names)
    }
