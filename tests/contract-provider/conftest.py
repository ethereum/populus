import pytest
import json


CONTRACT_MATH_CODE = "0x606060405261022e806100126000396000f360606040523615610074576000357c01000000000000000000000000000000000000000000000000000000009004806316216f391461007657806361bc221a146100995780637cf5dab0146100bc578063a5f3c23b146100e8578063d09de08a1461011d578063dcf537b11461014057610074565b005b610083600480505061016c565b6040518082815260200191505060405180910390f35b6100a6600480505061017f565b6040518082815260200191505060405180910390f35b6100d26004808035906020019091905050610188565b6040518082815260200191505060405180910390f35b61010760048080359060200190919080359060200190919050506101ea565b6040518082815260200191505060405180910390f35b61012a6004805050610201565b6040518082815260200191505060405180910390f35b6101566004808035906020019091905050610217565b6040518082815260200191505060405180910390f35b6000600d9050805080905061017c565b90565b60006000505481565b6000816000600082828250540192505081905550600060005054905080507f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c5816040518082815260200191505060405180910390a18090506101e5565b919050565b6000818301905080508090506101fb565b92915050565b600061020d6001610188565b9050610214565b90565b60006007820290508050809050610229565b91905056"


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
def MATH(MATH_ABI, MATH_CODE, MATH_RUNTIME, MATH_SOURCE):
    return {
        'abi': MATH_ABI,
        'code': MATH_CODE,
        'code_runtime': MATH_RUNTIME,
        'source': MATH_SOURCE,
    }


CONTRACT_MATH_V2_CODE = "0x606060405261017e806100126000396000f36060604052361561006c5760e060020a600035046316216f39811461006e5780632baeceb7146100775780633a9ebefd1461008657806361bc221a1461009d5780637cf5dab0146100a6578063a5f3c23b146100f6578063d09de08a14610110578063dcf537b11461011f575b005b6100fe600d5b90565b6100fe600061012e600161008d565b6100fe6004355b6000805482111561013557610002565b6100fe60005481565b6100fe6004355b60008054820181556040805183815290517f3496c3ede4ec3ab3686712aa1c238593ea6a42df83f98a5ec7df9834cfa577c59181900360200190a160006000505490505b919050565b602435600435015b60408051918252519081900360200190f35b6100fe600061012e60016100ad565b6100fe600435600781026100f1565b9050610074565b6000805483900390556040805183815290517f4fa5877b6c8d448ebaefa4048625aee504905823a70902d5f9a10a0b6ef0e1279181900360200190a160006000505490506100f156"

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
def MATH_V2_CODE():
    return CONTRACT_MATH_V2_CODE


@pytest.fixture(scope="session")
def MATH_V2_RUNTIME():
    return CONTRACT_MATH_V2_RUNTIME


@pytest.fixture(scope="session")
def MATH_V2_SOURCE():
    return CONTRACT_MATH_V2_SOURCE


@pytest.fixture(scope="session")
def MATH_V2_ABI():
    return CONTRACT_MATH_V2_ABI


@pytest.fixture()
def MATH_V2(MATH_V2_ABI, MATH_V2_CODE, MATH_V2_RUNTIME, MATH_V2_SOURCE):
    return {
        'abi': MATH_V2_ABI,
        'code': MATH_V2_CODE,
        'code_runtime': MATH_V2_RUNTIME,
        'source': MATH_V2_SOURCE,
    }


MULTIPLY13_LIBRARY_SOURCE = ("""
library Library13 {
    function multiply13(uint v) constant returns (uint) {
        return v * 13;
    }
}
""").strip()

MULTIPLY13_LIBRARY_CODE = "0x6060604052607c8060106000396000f36503059da08ac35060606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c4214604157603d565b6007565b60556004808035906020019091905050606b565b6040518082815260200191505060405180910390f35b6000600d820290506077565b91905056"

MULTIPLY13_LIBRARY_RUNTIME = "0x6503059da08ac35060606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c4214604157603d565b6007565b60556004808035906020019091905050606b565b6040518082815260200191505060405180910390f35b6000600d820290506077565b91905056"

MULTIPLY13_LIBRARY_ABI = json.loads('[{"constant":true,"inputs":[{"name":"value","type":"uint256"}],"name":"multiply13","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')


@pytest.fixture()
def LIBRARY_13_SOURCE():
    return MULTIPLY13_LIBRARY_SOURCE


@pytest.fixture()
def LIBRARY_13_CODE():
    return MULTIPLY13_LIBRARY_CODE


@pytest.fixture()
def LIBRARY_13_RUNTIME():
    return MULTIPLY13_LIBRARY_RUNTIME


@pytest.fixture()
def LIBRARY_13_ABI():
    return MULTIPLY13_LIBRARY_ABI


@pytest.fixture()
def LIBRARY_13(LIBRARY_13_CODE,
               LIBRARY_13_SOURCE,
               LIBRARY_13_RUNTIME,
               LIBRARY_13_ABI):
    return {
        'code': LIBRARY_13_CODE,
        'code_runtime': LIBRARY_13_RUNTIME,
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

MULTIPLY13_CONTRACT_CODE = "0x606060405260db8060106000396000f360606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c42146037576035565b005b604b60048080359060200190919050506061565b6040518082815260200191505060405180910390f35b600073__Library13_____________________________63cdbf9c4283604051827c0100000000000000000000000000000000000000000000000000000000028152600401808281526020019150506020604051808303818660325a03f41560025750505060405180519060200150905060d6565b91905056"

MULTIPLY13_CONTRACT_RUNTIME = "0x60606040526000357c010000000000000000000000000000000000000000000000000000000090048063cdbf9c42146037576035565b005b604b60048080359060200190919050506061565b6040518082815260200191505060405180910390f35b600073__Library13_____________________________63cdbf9c4283604051827c0100000000000000000000000000000000000000000000000000000000028152600401808281526020019150506020604051808303818660325a03f41560025750505060405180519060200150905060d6565b91905056"

MULTIPLY13_CONTRACT_ABI = json.loads('[{"constant":true,"inputs":[{"name":"v","type":"uint256"}],"name":"multiply13","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')


@pytest.fixture()
def MULTIPLY_13_SOURCE():
    return MULTIPLY13_CONTRACT_SOURCE


@pytest.fixture()
def MULTIPLY_13_CODE():
    return MULTIPLY13_CONTRACT_CODE


@pytest.fixture()
def MULTIPLY_13_RUNTIME():
    return MULTIPLY13_CONTRACT_RUNTIME


@pytest.fixture()
def MULTIPLY_13_ABI():
    return MULTIPLY13_CONTRACT_ABI


@pytest.fixture()
def MULTIPLY_13(MULTIPLY_13_CODE,
                MULTIPLY_13_RUNTIME,
                MULTIPLY_13_ABI,
                MULTIPLY_13_SOURCE):
    return {
        'code': MULTIPLY_13_CODE,
        'code_runtime': MULTIPLY_13_RUNTIME,
        'abi': MULTIPLY_13_ABI,
        'source': MULTIPLY_13_SOURCE,
    }
