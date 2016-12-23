import os
import json

from populus.utils.filesystem import (
    get_compiled_contracts_file_path,
    recursive_find_files,
    DEFAULT_CONTRACTS_DIR
)
from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)


def parse_solc_options_from_config(config, substitutions, section_name="solc"):
    """Parse out [solc] config section.

    :param config: py:class:`populus.config.Config` instance.

    :param substitutions: Dictionary of variable substitutions in path.
        Example ``{"project_dir": "/foobar"}

    :param section_name: Alternative solc config section name

    :return: dict of kwargs options to be passed to :py:func:`solc.wrapper.solc_wrapper`
    """

    if not config.has_section("solc"):
        # No special solc options given
        return {}

    options = {}

    remappings = config.get(section_name, "remappings")
    if remappings:
        remappings = remappings.split()
        remappings = [r.strip().format(**substitutions) for r in remappings if r.strip()]
        options["remappings"] = remappings

    return options


def find_project_contracts(project_dir, contracts_rel_dir=DEFAULT_CONTRACTS_DIR):
    contracts_dir = os.path.join(project_dir, contracts_rel_dir)

    return tuple(
        os.path.relpath(p) for p in recursive_find_files(contracts_dir, "*.sol")
    )


def write_compiled_sources(project_dir, compiled_sources):
    compiled_contract_path = get_compiled_contracts_file_path(project_dir)

    with open(compiled_contract_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': '))
        )
    return compiled_contract_path


def compile_project_contracts(project_dir, contracts_dir, **compiler_kwargs):
    compiler_kwargs.setdefault('output_values', ['bin', 'bin-runtime', 'abi'])
    contract_source_paths = find_project_contracts(project_dir, contracts_dir)
    try:
        compiled_sources = compile_files(contract_source_paths, **compiler_kwargs)
    except ContractsNotFound:
        return contract_source_paths, {}

    return contract_source_paths, compiled_sources


def compile_and_write_contracts(project_dir, contracts_dir, **compiler_kwargs):
    contract_source_paths, compiled_sources = compile_project_contracts(
        project_dir,
        contracts_dir,
        **compiler_kwargs
    )

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
