import textwrap
import json

import os

from populus.utils.config import Config
from populus.utils.filesystem import DEFAULT_CONTRACTS_DIR
from populus.compilation import (
    compile_and_write_contracts,
    parse_solc_options_from_config,
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')


CONTRACT_A_SOURCE = textwrap.dedent(("""
    import "foobaz/ContractB.sol";

    contract A is B {
    }
"""))


CONTRACT_B_SOURCE = textwrap.dedent(("""
    contract B {
        function doit() {}
    }
"""))


REMAPPINGS = """
foobaz={project_dir}/foobar
"""


def test_compile_with_remappings(project_dir, write_project_file):

    config = Config()
    config.add_section("solc")
    config.set("solc", "remappings", REMAPPINGS)

    write_project_file('contracts/ContractA.sol', CONTRACT_A_SOURCE)
    write_project_file('foobar/ContractB.sol', CONTRACT_B_SOURCE)

    substitutions = {
        "project_dir": project_dir
    }

    compiler_kwargs = parse_solc_options_from_config(config, substitutions)

    source_paths, compiled_sources, outfile_path = \
        compile_and_write_contracts(project_dir, DEFAULT_CONTRACTS_DIR, **compiler_kwargs)

    with open(outfile_path) as outfile:
        compiled_contract_data = json.load(outfile)

    assert 'A' in compiled_contract_data
    assert 'B' in compiled_contract_data
