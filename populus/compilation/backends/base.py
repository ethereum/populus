import json

from eth_utils import (
    is_string,
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


