import pytest

import json

from populus.utils.compat import (
    Timeout,
)
from populus.utils.linking import (
    link_bytecode_by_name,
)
from populus import Project


CONTRACT_MATH_BYTECODE = "0x606060405261022e806100126000396000f360606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"


CONTRACT_MATH_RUNTIME = "0x60606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"


CONTRACT_MATH_SOURCE = ("""
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
""").strip()

CONTRACT_MATH_ABI = json.loads('[{"constant":false,"inputs":[],"name":"return13","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":true,"inputs":[],"name":"counter","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"uint256"}],"name":"increment","outputs":[{"name":"result","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"},{"name":"b","type":"int256"}],"name":"add","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":false,"inputs":[],"name":"increment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"}],"name":"multiply7","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"value","type":"uint256"}],"name":"Increased","type":"event"}]')  # NOQA


@pytest.fixture(scope="session")
def MATH_BYTECODE():
    return CONTRACT_MATH_BYTECODE


@pytest.fixture(scope="session")
def MATH_RUNTIME():
    return CONTRACT_MATH_RUNTIME


@pytest.fixture(scope="session")
def MATH_SOURCE():
    return CONTRACT_MATH_SOURCE


@pytest.fixture(scope="session")
def MATH_ABI():
    return CONTRACT_MATH_ABI


@pytest.fixture(scope='session')
def MATH(MATH_ABI, MATH_BYTECODE, MATH_RUNTIME, MATH_SOURCE):
    return {
        'abi': MATH_ABI,
        'bytecode': MATH_BYTECODE,
        'bytecode_runtime': MATH_RUNTIME,
        'source': MATH_SOURCE,
    }


CONTRACT_MATH_V2_BYTECODE = "0x606060405261017e806100126000396000f36060604052361561006c5760e060020a600035046316216f39811461006e5780632baeceb7146100775780633a9ebefd1461008657806361bc221a1461009d5780637cf5dab0146100a6578063a5f3c23b146100f6578063d09de08a14610110578063dcf537b11461011f575b005b6100fe600d5b90565b6100fe600061012e600161008d565b6100fe6004355b6000805482111561013557610002565b6100fe60005481565b6100fe6004355b60008054820181556040805183815290517f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c59181900360200190a160006000505490505b919050565b602435600435015b60408051918252519081900360200190f35b6100fe600061012e60016100ad565b6100fe600435600781026100f1565b9050610074565b6000805483900390556040805183815290517f4fa5877b6c8d448ebaefa4048625aee504905823a70902d5f9a10a0b6ef0e1279181900360200190a160006000505490506100f156"

CONTRACT_MATH_V2_RUNTIME = "0x6060604052361561006c5760e060020a600035046316216f39811461006e5780632baeceb7146100775780633a9ebefd1461008657806361bc221a1461009d5780637cf5dab0146100a6578063a5f3c23b146100f6578063d09de08a14610110578063dcf537b11461011f575b005b6100fe600d5b90565b6100fe600061012e600161008d565b6100fe6004355b6000805482111561013557610002565b6100fe60005481565b6100fe6004355b60008054820181556040805183815290517f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c59181900360200190a160006000505490505b919050565b602435600435015b60408051918252519081900360200190f35b6100fe600061012e60016100ad565b6100fe600435600781026100f1565b9050610074565b6000805483900390556040805183815290517f4fa5877b6c8d448ebaefa4048625aee504905823a70902d5f9a10a0b6ef0e1279181900360200190a160006000505490506100f156"

CONTRACT_MATH_V2_SOURCE = ("""
contract Math {
    uint public counter;

    event Increased(uint value);
    event Decreased(uint value);

    function increment() public returns (uint) {
        return increment(1);
    }

    function increment(uint amt) public returns (uint) {
        counter += amt;
        Increased(amt);
        return counter;
    }

    function decrement() public returns (uint) {
        return decrement(1);
    }

    function decrement(uint amt) public returns (uint) {
        if (amt > counter) throw;
        counter -= amt;
        Decreased(amt);
        return counter;
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
""").strip()

CONTRACT_MATH_V2_ABI = json.loads('[{"constant":false,"inputs":[],"name":"return13","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":false,"inputs":[],"name":"decrement","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"uint256"}],"name":"decrement","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"counter","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"uint256"}],"name":"increment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"},{"name":"b","type":"int256"}],"name":"add","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"constant":false,"inputs":[],"name":"increment","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"a","type":"int256"}],"name":"multiply7","outputs":[{"name":"result","type":"int256"}],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"value","type":"uint256"}],"name":"Increased","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"value","type":"uint256"}],"name":"Decreased","type":"event"}]')  # NOQA


@pytest.fixture(scope="session")
def MATH_V2_BYTECODE():
    return CONTRACT_MATH_V2_BYTECODE


@pytest.fixture(scope="session")
def MATH_V2_RUNTIME():
    return CONTRACT_MATH_V2_RUNTIME


@pytest.fixture(scope="session")
def MATH_V2_SOURCE():
    return CONTRACT_MATH_V2_SOURCE


@pytest.fixture(scope="session")
def MATH_V2_ABI():
    return CONTRACT_MATH_V2_ABI


@pytest.fixture(scope='session')
def MATH_V2(MATH_V2_ABI, MATH_V2_BYTECODE, MATH_V2_RUNTIME, MATH_V2_SOURCE):
    return {
        'abi': MATH_V2_ABI,
        'bytecode': MATH_V2_BYTECODE,
        'bytecode_runtime': MATH_V2_RUNTIME,
        'source': MATH_V2_SOURCE,
    }


MULTIPLY13_LIBRARY_SOURCE = ("""
library Library13 {
    function multiply13(uint v) constant returns (uint) {
        return v * 13;
    }
}
""").strip()

MULTIPLY13_LIBRARY_BYTECODE = "0x6060604052607c8060106000396000f36503059da08ac35060606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c4214604157603d565b6007565b60556004808035906020019091905050606b565b6040518082815260200191505060405180910390f35b6000600d820290506077565b91905056"

MULTIPLY13_LIBRARY_RUNTIME = "0x6503059da08ac35060606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c4214604157603d565b6007565b60556004808035906020019091905050606b565b6040518082815260200191505060405180910390f35b6000600d820290506077565b91905056"

MULTIPLY13_LIBRARY_ABI = json.loads('[{"constant":true,"inputs":[{"name":"value","type":"uint256"}],"name":"multiply13","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')


@pytest.fixture(scope='session')
def LIBRARY_13_SOURCE():
    return MULTIPLY13_LIBRARY_SOURCE


@pytest.fixture(scope='session')
def LIBRARY_13_BYTECODE():
    return MULTIPLY13_LIBRARY_BYTECODE


@pytest.fixture(scope='session')
def LIBRARY_13_RUNTIME():
    return MULTIPLY13_LIBRARY_RUNTIME


@pytest.fixture(scope='session')
def LIBRARY_13_ABI():
    return MULTIPLY13_LIBRARY_ABI


@pytest.fixture(scope='session')
def LIBRARY_13(LIBRARY_13_BYTECODE,
               LIBRARY_13_SOURCE,
               LIBRARY_13_RUNTIME,
               LIBRARY_13_ABI):
    return {
        'bytecode': LIBRARY_13_BYTECODE,
        'bytecode_runtime': LIBRARY_13_RUNTIME,
        'abi': LIBRARY_13_ABI,
        'source': LIBRARY_13_SOURCE,
    }


MULTIPLY13_CONTRACT_SOURCE = ("""
contract Multiply13 {
    function multiply13(uint v) constant returns (uint) {
        return Library13.multiply13(v);
    }
}
""").strip()

MULTIPLY13_CONTRACT_BYTECODE = "0x606060405260db8060106000396000f360606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c42146037576035565b005b604b60048080359060200190919050506061565b6040518082815260200191505060405180910390f35b600073__Library13_____________________________63cdbf9c4283604051827c0100000000000000000000000000000000000000000000000000000000028152600401808281526020019150506020604051808303818660325a03f41560025750505060405180519060200150905060d6565b91905056"

MULTIPLY13_CONTRACT_RUNTIME = "0x60606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c42146037576035565b005b604b60048080359060200190919050506061565b6040518082815260200191505060405180910390f35b600073__Library13_____________________________63cdbf9c4283604051827c0100000000000000000000000000000000000000000000000000000000028152600401808281526020019150506020604051808303818660325a03f41560025750505060405180519060200150905060d6565b91905056"

MULTIPLY13_CONTRACT_ABI = json.loads('[{"constant":true,"inputs":[{"name":"v","type":"uint256"}],"name":"multiply13","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')


@pytest.fixture(scope='session')
def MULTIPLY_13_SOURCE():
    return MULTIPLY13_CONTRACT_SOURCE


@pytest.fixture(scope='session')
def MULTIPLY_13_BYTECODE():
    return MULTIPLY13_CONTRACT_BYTECODE


@pytest.fixture(scope='session')
def MULTIPLY_13_RUNTIME():
    return MULTIPLY13_CONTRACT_RUNTIME


@pytest.fixture(scope='session')
def MULTIPLY_13_ABI():
    return MULTIPLY13_CONTRACT_ABI


@pytest.fixture(scope='session')
def MULTIPLY_13(MULTIPLY_13_BYTECODE,
                MULTIPLY_13_RUNTIME,
                MULTIPLY_13_ABI,
                MULTIPLY_13_SOURCE):
    return {
        'bytecode': MULTIPLY_13_BYTECODE,
        'bytecode_runtime': MULTIPLY_13_RUNTIME,
        'abi': MULTIPLY_13_ABI,
        'source': MULTIPLY_13_SOURCE,
    }


@pytest.yield_fixture()
def temp_chain(project_dir, write_project_file, MATH, LIBRARY_13, MULTIPLY_13, wait_for_unlock):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file(
        'contracts/Multiply13.sol',
        '\n'.join((LIBRARY_13['source'], MULTIPLY_13['source'])),
    )

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    with project.get_chain('temp') as chain:
        wait_for_unlock(chain.web3)
        yield chain


@pytest.fixture()
def math(temp_chain):
    chain = temp_chain
    web3 = chain.web3

    Math = chain.contract_factories.Math
    MATH = chain.project.compiled_contracts['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = chain.wait.for_contract_address(math_deploy_txn_hash)

    assert math_deploy_txn['input'] == MATH['bytecode']
    assert web3.eth.getCode(math_address) == MATH['bytecode_runtime']

    return Math(address=math_address)


@pytest.fixture()
def library_13(temp_chain):
    chain = temp_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash)

    assert library_deploy_txn['input'] == LIBRARY_13['bytecode']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['bytecode_runtime']

    return Library13(address=library_13_address)


@pytest.fixture()
def multiply_13(temp_chain, library_13):
    chain = temp_chain
    web3 = chain.web3

    Multiply13 = chain.contract_factories['Multiply13']

    bytecode = link_bytecode_by_name(Multiply13.bytecode, Library13=library_13.address)
    bytecode_runtime = link_bytecode_by_name(Multiply13.bytecode_runtime, Library13=library_13.address)

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13.abi,
        bytecode=bytecode,
        bytecode_runtime=bytecode_runtime,
        source=Multiply13.source,
    )

    multiply_13_deploy_txn_hash = LinkedMultiply13.deploy()
    multiply_13_deploy_txn = web3.eth.getTransaction(multiply_13_deploy_txn_hash)
    multiply_13_address = chain.wait.for_contract_address(multiply_13_deploy_txn_hash)

    assert multiply_13_deploy_txn['input'] == LinkedMultiply13.bytecode
    assert web3.eth.getCode(multiply_13_address) == LinkedMultiply13.bytecode_runtime

    return LinkedMultiply13(address=multiply_13_address)


@pytest.fixture()
def register_address(temp_chain):
    chain = temp_chain

    def _register_address(name, value):
        register_txn_hash = temp_chain.registrar.transact().setAddress(
            'contract/{name}'.format(name=name), value,
        )
        chain.wait.for_receipt(register_txn_hash)
    return _register_address
