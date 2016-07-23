import pytest
import json
import textwrap


CONTRACT_MATH_CODE = b"0x606060405261022e806100126000396000f360606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"


CONTRACT_MATH_RUNTIME = b"0x60606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"


CONTRACT_MATH_SOURCE = textwrap.dedent(("""
    contract Math {
        uint public counter;

        event Increased(uint value);

        function increment() public returns (uint) {
            return increment(1);
        }

        function increment(uint amt) public returns (uint result) {
            counter += amt;
            result = counter;
            Increased(result);
            return result;
        }

        function add(int a, int b) public returns (int result) {
            result = a + b;
            return result;
        }

        function multiply7(int a) public returns (int result) {
            result = a * 7;
            return result;
        }

        function return13() public returns (int result) {
            result = 13;
            return result;
        }
    }
""")).strip()

CONTRACT_MATH_ABI = json.loads('[{"constant":false,"inputs":[],"name":"return13","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":true,"inputs":[],"name":"counter","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"uint256"}],"name":"increment","outputs":[{"name":"result","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"},{"name":"b","type":"int256"}],"name":"add","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":false,"inputs":[],"name":"increment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"}],"name":"multiply7","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"value","type":"uint256"}],"name":"Increased","type":"event"}]')  # NOQA


@pytest.fixture(scope="session")
def MATH_CODE():
    return CONTRACT_MATH_CODE


@pytest.fixture(scope="session")
def MATH_RUNTIME():
    return CONTRACT_MATH_RUNTIME


@pytest.fixture(scope="session")
def MATH_SOURCE():
    return CONTRACT_MATH_SOURCE


@pytest.fixture(scope="session")
def MATH_ABI():
    return CONTRACT_MATH_ABI


@pytest.fixture()
def MathContract(web3_tester, MATH_ABI, MATH_CODE, MATH_RUNTIME, MATH_SOURCE):
    return web3_tester.eth.contract(
        abi=MATH_ABI,
        code=MATH_CODE,
        code_runtime=MATH_RUNTIME,
        source=MATH_SOURCE,
    )


CONTRACT_SIMPLE_CONSTRUCTOR_SOURCE = "contract WithNoArgumentConstructor { uint public data; function WithNoArgumentConstructor() { data = 3; }}"
CONTRACT_SIMPLE_CONSTRUCTOR_CODE = b'0x60606040526003600055602c8060156000396000f3606060405260e060020a600035046373d4a13a8114601a575b005b602260005481565b6060908152602090f3'
CONTRACT_SIMPLE_CONSTRUCTOR_RUNTIME = b'0x606060405260e060020a600035046373d4a13a8114601a575b005b602260005481565b6060908152602090f3'
CONTRACT_SIMPLE_CONSTRUCTOR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"data","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"inputs":[],"type":"constructor"}]')


@pytest.fixture(scope="session")
def SIMPLE_CONSTRUCTOR_SOURCE():
    return CONTRACT_SIMPLE_CONSTRUCTOR_SOURCE


@pytest.fixture(scope="session")
def SIMPLE_CONSTRUCTOR_CODE():
    return CONTRACT_SIMPLE_CONSTRUCTOR_CODE


@pytest.fixture(scope="session")
def SIMPLE_CONSTRUCTOR_RUNTIME():
    return CONTRACT_SIMPLE_CONSTRUCTOR_RUNTIME


@pytest.fixture(scope="session")
def SIMPLE_CONSTRUCTOR_ABI():
    return CONTRACT_SIMPLE_CONSTRUCTOR_ABI


@pytest.fixture()
def SimpleConstructorContract(web3_tester,
                              SIMPLE_CONSTRUCTOR_SOURCE,
                              SIMPLE_CONSTRUCTOR_CODE,
                              SIMPLE_CONSTRUCTOR_RUNTIME,
                              SIMPLE_CONSTRUCTOR_ABI):
    return web3_tester.eth.contract(
        abi=SIMPLE_CONSTRUCTOR_ABI,
        code=SIMPLE_CONSTRUCTOR_CODE,
        code_runtime=SIMPLE_CONSTRUCTOR_RUNTIME,
        source=SIMPLE_CONSTRUCTOR_SOURCE,
    )


CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_SOURCE =  "contract WithConstructorArguments { uint public data_a; bytes32 public data_b; function WithConstructorArguments(uint a, bytes32 b) { data_a = a; data_b = b; }}"

CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_CODE = b"0x60606040818152806066833960a09052516080516000918255600155603e908190602890396000f3606060405260e060020a600035046388ec134681146024578063d4c46c7614602c575b005b603460005481565b603460015481565b6060908152602090f3"
CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_RUNTIME = b"0x606060405260e060020a600035046388ec134681146024578063d4c46c7614602c575b005b603460005481565b603460015481565b6060908152602090f3"
CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_ABI = json.loads('[{"constant":true,"inputs":[],"name":"data_a","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"data_b","outputs":[{"name":"","type":"bytes32"}],"type":"function"},{"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"bytes32"}],"type":"constructor"}]')


@pytest.fixture()
def WITH_CONSTRUCTOR_ARGUMENTS_SOURCE():
    return CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_SOURCE


@pytest.fixture()
def WITH_CONSTRUCTOR_ARGUMENTS_CODE():
    return CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_CODE


@pytest.fixture()
def WITH_CONSTRUCTOR_ARGUMENTS_RUNTIME():
    return CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_RUNTIME


@pytest.fixture()
def WITH_CONSTRUCTOR_ARGUMENTS_ABI():
    return CONTRACT_WITH_CONSTRUCTOR_ARGUMENTS_ABI


@pytest.fixture()
def WithConstructorArgumentsContract(web3_tester,
                                     WITH_CONSTRUCTOR_ARGUMENTS_SOURCE,
                                     WITH_CONSTRUCTOR_ARGUMENTS_CODE,
                                     WITH_CONSTRUCTOR_ARGUMENTS_RUNTIME,
                                     WITH_CONSTRUCTOR_ARGUMENTS_ABI):
    return web3_tester.eth.contract(
        abi=WITH_CONSTRUCTOR_ARGUMENTS_ABI,
        code=WITH_CONSTRUCTOR_ARGUMENTS_CODE,
        code_runtime=WITH_CONSTRUCTOR_ARGUMENTS_RUNTIME,
        source=WITH_CONSTRUCTOR_ARGUMENTS_SOURCE,
    )


CONTRACT_EMITTER_SOURCE = textwrap.dedent(("""
contract Emitter {
    event LogAnonymous() anonymous;
    event LogNoArguments();
    event LogSingleArg(uint arg0);
    event LogDoubleArg(uint arg0, uint arg1);
    event LogTripleArg(uint arg0, uint arg1, uint arg2);
    event LogQuadrupleArg(uint arg0, uint arg1, uint arg2, uint arg3);

    // Indexed
    event LogSingleWithIndex(uint indexed arg0);
    event LogDoubleWithIndex(uint arg0, uint indexed arg1);
    event LogTripleWithIndex(uint arg0, uint indexed arg1, uint indexed arg2);
    event LogQuadrupleWithIndex(uint arg0, uint arg1, uint indexed arg2, uint indexed arg3);

    enum WhichEvent {
        LogAnonymous,
        LogNoArguments,
        LogSingleArg,
        LogDoubleArg,
        LogTripleArg,
        LogQuadrupleArg,
        LogSingleWithIndex,
        LogDoubleWithIndex,
        LogTripleWithIndex,
        LogQuadrupleWithIndex
    }

    function logNoArgs(WhichEvent which) public {
        if (which == WhichEvent.LogNoArguments) LogNoArguments();
        else if (which == WhichEvent.LogAnonymous) LogAnonymous();
        else throw;
    }

    function logSingle(WhichEvent which, uint arg0) public {
        if (which == WhichEvent.LogSingleArg) LogSingleArg(arg0);
        else if (which == WhichEvent.LogSingleWithIndex) LogSingleWithIndex(arg0);
        else throw;
    }

    function logDouble(WhichEvent which, uint arg0, uint arg1) public {
        if (which == WhichEvent.LogDoubleArg) LogDoubleArg(arg0, arg1);
        else if (which == WhichEvent.LogDoubleWithIndex) LogDoubleWithIndex(arg0, arg1);
        else throw;
    }

    function logTriple(WhichEvent which, uint arg0, uint arg1, uint arg2) public {
        if (which == WhichEvent.LogTripleArg) LogTripleArg(arg0, arg1, arg2);
        else if (which == WhichEvent.LogTripleWithIndex) LogTripleWithIndex(arg0, arg1, arg2);
        else throw;
    }

    function logQuadruple(WhichEvent which, uint arg0, uint arg1, uint arg2, uint arg3) public {
        if (which == WhichEvent.LogQuadrupleArg) LogQuadrupleArg(arg0, arg1, arg2, arg3);
        else if (which == WhichEvent.LogQuadrupleWithIndex) LogQuadrupleWithIndex(arg0, arg1, arg2, arg3);
        else throw;
    }
}
"""))

CONTRACT_EMITTER_CODE = "0x60606040526102c0806100126000396000f3606060405260e060020a600035046317c0c180811461004757806320f0256e1461008057806390b41d8b146100da5780639c37705314610125578063aa6fd82214610177575b005b61004560043560018114156101b9577f1e86022f78f8d04f8e3dfd13a2bdb280403e6632877c0dbee5e4eeb259908a5c60006060a15b50565b61004560043560243560443560643560843560058514156101d1576060848152608084815260a084905260c08390527ff039d147f23fe975a4254bdf6b1502b8c79132ae1833986b7ccef2638e73fdf991a15b5050505050565b610045600435602435604435600383141561021357606082815260808290527fdf0cb1dea99afceb3ea698d62e705b736f1345a7eee9eb07e63d1f8f556c1bc590604090a15b505050565b610045600435602435604435606435600484141561024e576060838152608083905260a08290527f4a25b279c7c585f25eda9788ac9420ebadae78ca6b206a0e6ab488fd81f550629080a15b50505050565b610045600435602435600282141561028b5760608181527f56d2ef3c5228bf5d88573621e325a4672ab50e033749a601e4f4a5e1dce905d490602090a15b5050565b60008114156101cc5760006060a061007d565b610002565b60098514156101cc5760608481526080849052819083907fa30ece802b64cd2b7e57dabf4010aabf5df26d1556977affb07b98a77ad955b590604090a36100d3565b60078314156101cc57606082815281907f057bc32826fbe161da1c110afcdcae7c109a8b69149f727fc37a603c60ef94ca90602090a2610120565b60088414156101cc576060838152819083907ff16c999b533366ca5138d78e85da51611089cd05749f098d6c225d4cd42ee6ec90602090a3610171565b60068214156101cc57807ff70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb1560006060a26101b556"

CONTRACT_EMITTER_RUNTIME = "0x606060405260e060020a600035046317c0c180811461004757806320f0256e1461008057806390b41d8b146100da5780639c37705314610125578063aa6fd82214610177575b005b61004560043560018114156101b9577f1e86022f78f8d04f8e3dfd13a2bdb280403e6632877c0dbee5e4eeb259908a5c60006060a15b50565b61004560043560243560443560643560843560058514156101d1576060848152608084815260a084905260c08390527ff039d147f23fe975a4254bdf6b1502b8c79132ae1833986b7ccef2638e73fdf991a15b5050505050565b610045600435602435604435600383141561021357606082815260808290527fdf0cb1dea99afceb3ea698d62e705b736f1345a7eee9eb07e63d1f8f556c1bc590604090a15b505050565b610045600435602435604435606435600484141561024e576060838152608083905260a08290527f4a25b279c7c585f25eda9788ac9420ebadae78ca6b206a0e6ab488fd81f550629080a15b50505050565b610045600435602435600282141561028b5760608181527f56d2ef3c5228bf5d88573621e325a4672ab50e033749a601e4f4a5e1dce905d490602090a15b5050565b60008114156101cc5760006060a061007d565b610002565b60098514156101cc5760608481526080849052819083907fa30ece802b64cd2b7e57dabf4010aabf5df26d1556977affb07b98a77ad955b590604090a36100d3565b60078314156101cc57606082815281907f057bc32826fbe161da1c110afcdcae7c109a8b69149f727fc37a603c60ef94ca90602090a2610120565b60088414156101cc576060838152819083907ff16c999b533366ca5138d78e85da51611089cd05749f098d6c225d4cd42ee6ec90602090a3610171565b60068214156101cc57807ff70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb1560006060a26101b556"

CONTRACT_EMITTER_ABI = json.loads('[{"constant":false,"inputs":[{"name":"which","type":"uint8"}],"name":"logNoArgs","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"},{"name":"arg2","type":"uint256"},{"name":"arg3","type":"uint256"}],"name":"logQuadruple","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"}],"name":"logDouble","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"},{"name":"arg2","type":"uint256"}],"name":"logTriple","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"}],"name":"logSingle","outputs":[],"type":"function"},{"anonymous":true,"inputs":[],"name":"LogAnonymous","type":"event"},{"anonymous":false,"inputs":[],"name":"LogNoArguments","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"}],"name":"LogSingleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"}],"name":"LogDoubleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":false,"name":"arg2","type":"uint256"}],"name":"LogTripleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":false,"name":"arg2","type":"uint256"},{"indexed":false,"name":"arg3","type":"uint256"}],"name":"LogQuadrupleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"arg0","type":"uint256"}],"name":"LogSingleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":true,"name":"arg1","type":"uint256"}],"name":"LogDoubleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":true,"name":"arg1","type":"uint256"},{"indexed":true,"name":"arg2","type":"uint256"}],"name":"LogTripleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":true,"name":"arg2","type":"uint256"},{"indexed":true,"name":"arg3","type":"uint256"}],"name":"LogQuadrupleWithIndex","type":"event"}]')


@pytest.fixture()
def EMITTER_SOURCE():
    return CONTRACT_EMITTER_SOURCE


@pytest.fixture()
def EMITTER_CODE():
    return CONTRACT_EMITTER_CODE


@pytest.fixture()
def EMITTER_RUNTIME():
    return CONTRACT_EMITTER_RUNTIME


@pytest.fixture()
def EMITTER_ABI():
    return CONTRACT_EMITTER_ABI


@pytest.fixture()
def EmitterContract(web3_tester,
                    EMITTER_SOURCE,
                    EMITTER_CODE,
                    EMITTER_RUNTIME,
                    EMITTER_ABI):
    return web3_tester.eth.contract(
        abi=EMITTER_ABI,
        code=EMITTER_CODE,
        code_runtime=EMITTER_RUNTIME,
        source=EMITTER_SOURCE,
    )
