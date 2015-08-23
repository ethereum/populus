import pytest

from populus.solidity import solc


contract_source = "contract Example { function Example() {}}"
contract_compiled_output = '{"contracts":{"Example":{"binary":"60606040525b5b600a8060136000396000f30060606040526008565b00","json-abi":"[{\\"inputs\\":[],\\"type\\":\\"constructor\\"}]\\n","natspec-dev":"{\\n   \\"methods\\" : {}\\n}\\n","natspec-user":"{\\n   \\"methods\\" : {}\\n}\\n","sol-abi":"contract Example{function Example();}"}}}\n\n'  # NOQA


def test_source_and_input_files_mutually_exclusive():
    with pytest.raises(ValueError):
        solc(source=contract_source, input_files=['someContract.sol'])


def test_one_of_source_or_input_files_required():
    with pytest.raises(ValueError):
        solc()


def test_source_compilation():
    code = solc(source=contract_source)
    assert code == contract_compiled_output


def test_file_compilation():
    code = solc(input_files=["tests/solidity/projects/test-01/contracts/Example.sol"])
    assert code == contract_compiled_output
