from populus.packages.build import (
    construct_contract_type_object,
)


CONTRACT_DATA = {
    'abi': [],
    'bytecode': '0x1234567890abcdef',
    'bytecode_runtime': '0xdeadbeef',
    'metadata': {
        'compiler': {
            'version': '0.4.2+commit.af6afb04.Darwin.appleclang',
        },
        'settings': {
            'optimizer': {
                'runs': 200,
                'enabled': True,
            }
        }
    },
    'userdoc': {
       "methods" : {
          "releaseFunds()" : {
             "notice" : "This will release the escrowed funds to the other party."
          }
       }
    },
    'devdoc': {
       "author" : "Piper Merriam <pipermerriam@gmail.com>",
       "methods" : {
          "releaseFunds()" : {
             "details" : "Releases the escrowed funds to the other party."
          }
       },
       "title" : "Contract for holding funds in escrow between two semi trusted parties."
    },
}


def test_construct_contract_type_object():
    contract_type_object = construct_contract_type_object(
        CONTRACT_DATA,
        'Math',
    )

    assert contract_type_object['bytecode'] == '0x1234567890abcdef'
    assert contract_type_object['runtime_bytecode'] == '0xdeadbeef'
    assert contract_type_object['contract_name'] == 'Math'
    assert contract_type_object['abi'] == []
    assert contract_type_object['natspec'] == {
       "author" : "Piper Merriam <pipermerriam@gmail.com>",
       "methods" : {
          "releaseFunds()" : {
             "details" : "Releases the escrowed funds to the other party.",
             "notice" : "This will release the escrowed funds to the other party."
          }
       },
       "title" : "Contract for holding funds in escrow between two semi trusted parties."
    }
