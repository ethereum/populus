import pytest

from populus.solidity import (
    solc,
    version_regex,
)


contract_source = "contract Example { function Example() {}}"
contract_compiled_raw = '{"contracts":{"Example":{"binary":"60606040525b5b600a8060136000396000f30060606040526008565b00","json-abi":"[{\\"inputs\\":[],\\"type\\":\\"constructor\\"}]\\n","natspec-dev":"{\\n   \\"methods\\" : {}\\n}\\n","natspec-user":"{\\n   \\"methods\\" : {}\\n}\\n","sol-abi":"contract Example{function Example();}"}}}\n\n'  # NOQA
contract_compiled_json = [('Example', {'natspec-user': {'methods': {}}, 'binary': '60606040525b5b600a8060136000396000f30060606040526008565b00', 'json-abi': [{'inputs': [], 'type': 'constructor'}], 'sol-abi': 'contract Example{function Example();}', 'natspec-dev': {'methods': {}}})]
contract_compiled_json_rich = {'Example': {'natspec-user': {'methods': {}}, 'binary': '60606040525b5b600a8060136000396000f30060606040526008565b00', 'json-abi': [{'inputs': [], 'type': 'constructor'}], 'sol-abi': 'contract Example{function Example();}', 'natspec-dev': {'methods': {}}}}



def test_source_and_input_files_mutually_exclusive():
    with pytest.raises(ValueError):
        solc(source=contract_source, input_files=['someContract.sol'])


def test_one_of_source_or_input_files_required():
    with pytest.raises(ValueError):
        solc()


def test_raw_source_compilation():
    code = solc(source=contract_source, raw=True)
    assert code == contract_compiled_raw


def test_raw_file_compilation():
    code = solc(input_files=["tests/solidity/projects/test-01/contracts/Example.sol"], raw=True)
    assert code == contract_compiled_raw


def test_json_source_compilation_not_rich():
    code = solc(source=contract_source, rich=False)
    assert code == contract_compiled_json


def test_json_source_compilation():
    code = solc(source=contract_source, rich=False)
    assert code == contract_compiled_json


def test_version_with_hash():
    version_string = 'solc, the solidity compiler commandline interface\nVersion: 0.1.1-054b3c3c/Release-Darwin/clang/JIT\n'
    version = version_regex.search(version_string).groups()[0]
    assert version == '0.1.1-054b3c3c'


def test_version_without_hash():
    version_string = 'solc, the solidity compiler commandline interface\nVersion: 0.1.1/Release-Darwin/clang/JIT\n'
    version = version_regex.search(version_string).groups()[0]
    assert version == '0.1.1'
