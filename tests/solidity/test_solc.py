import os
import pytest
import json

from populus.solidity import (
    solc,
    version_regex,
    is_solc_available,
)

skip_if_no_sol_compiler = pytest.mark.skipif(
    not is_solc_available(),
    reason="'solc' compiler not available",
)

this_dir = os.path.dirname(__file__)

contract_source = "contract Example { function Example() {}}"
contract_compiled_raw = '{"contracts":{"Example":{"abi":"[{\\"inputs\\":[],\\"type\\":\\"constructor\\"}]\\n","bin":"60606040525b5b600a8060126000396000f360606040526008565b00","bin-runtime":"60606040526008565b00","devdoc":"{\\n   \\"methods\\" : {}\\n}\\n","userdoc":"{\\n   \\"methods\\" : {}\\n}\\n"}},"version":"0.1.3-1736fe80/RelWithDebInfo-Darwin/unknown/JIT linked to libethereum-0.9.92-dcf2fd11/RelWithDebInfo-Darwin/unknown/JIT"}\n\n'  # NOQA
contract_compiled_json = [('Example', {'bin': '60606040525b5b600a8060126000396000f360606040526008565b00', "bin-runtime": "60606040526008565b00", 'abi': [{'inputs': [], 'type': 'constructor'}], 'userdoc': {'methods': {}}, 'devdoc': {'methods': {}}})]  # NOQA
contract_compiled_json_rich = {'Example': {'natspec-user': {'methods': {}}, 'binary': '60606040525b5b600a8060136000396000f30060606040526008565b00', 'json-abi': [{'inputs': [], 'type': 'constructor'}], 'sol-abi': 'contract Example{function Example();}', 'natspec-dev': {'methods': {}}}}


def test_source_and_input_files_mutually_exclusive():
    with pytest.raises(ValueError):
        solc(source=contract_source, input_files=['someContract.sol'])


def test_one_of_source_or_input_files_required():
    with pytest.raises(ValueError):
        solc()


def cmp_compile_data(a, b):
    assert set(a.keys()) == set(b.keys())
    for k in a.keys():
        a_value = a[k]
        b_value = b[k]
        if k == "version":
            assert a_value and b_value
        else:
            assert a_value == b_value


@skip_if_no_sol_compiler
def test_raw_source_compilation():
    code = solc(source=contract_source, raw=True)
    cmp_compile_data(json.loads(code), json.loads(contract_compiled_raw))


@skip_if_no_sol_compiler
def test_raw_file_compilation():
    input_file = os.path.join(this_dir, "projects/test-01/contracts/Example.sol")
    code = solc(input_files=[input_file], raw=True)
    cmp_compile_data(json.loads(code), json.loads(contract_compiled_raw))


@skip_if_no_sol_compiler
def test_json_source_compilation_not_rich():
    code = solc(source=contract_source, rich=False)
    for left, right in zip(code, contract_compiled_json):
        assert left[0] == right[0]
        cmp_compile_data(left[1], right[1])


@skip_if_no_sol_compiler
def test_json_source_compilation():
    code = solc(source=contract_source, rich=False)
    for left, right in zip(code, contract_compiled_json):
        assert left[0] == right[0]
        cmp_compile_data(left[1], right[1])


def test_version_with_hash():
    version_string = 'solc, the solidity compiler commandline interface\nVersion: 0.1.1-054b3c3c/Release-Darwin/clang/JIT\n'
    version = version_regex.search(version_string).groups()[0]
    assert version == '0.1.1-054b3c3c'


def test_version_without_hash():
    version_string = 'solc, the solidity compiler commandline interface\nVersion: 0.1.1/Release-Darwin/clang/JIT\n'
    version = version_regex.search(version_string).groups()[0]
    assert version == '0.1.1'
