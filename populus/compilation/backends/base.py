import json

from eth_utils import (
    is_string,
)

from populus.utils.deploy import compute_deploy_order
from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
)


class BaseCompilerBackend(object):
    compiler_settings = None

    def __init__(self, settings):
        self.compiler_settings = settings

    def get_compiled_contract_data(self, source_file_paths, import_remappings):
        raise NotImplementedError("Must be implemented by subclasses")


def _load_json_if_string(value):
    if is_string(value):
        return json.loads(value)
    else:
        return value


def _normalize_contract_metadata(metadata):
    if not metadata:
        return None
    elif is_string(metadata):
        return json.loads(metadata)
    else:
        raise ValueError("Unknown metadata format '{0}'".format(metadata))


def add_dependency_info(compiled_contracts):
    dependency_graph = get_shallow_dependency_graph(
        compiled_contracts,
    )

    deploy_order = compute_deploy_order(dependency_graph)

    for name, contract in compiled_contracts.items():
        deps = get_recursive_contract_dependencies(
            name,
            dependency_graph,
        )
        contract['ordered_dependencies'] = [cid for cid in deploy_order if cid in deps]

