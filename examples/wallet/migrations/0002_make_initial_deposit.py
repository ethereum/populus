# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from populus import migrations


class Migration(migrations.Migration):

    migration_id = '0002_make_initial_deposit'
    dependencies = [
        '0001_deploy_wallet_contract',
    ]
    operations = [
        migrations.TransactContract(
            contract_name='Wallet',
            method_name='deposit',
            transaction={'value': 5000000000000000000},  # 5 ether
            contract_address=migrations.Address.defer(key="contract/Wallet"),
        )
    ]
    compiled_contracts = {
        'Wallet': {
            'abi': [
                {
                    'constant': False,
                    'inputs': [
                        {
                            'name': 'value',
                            'type': 'uint256',
                        },
                    ],
                    'name': 'withdraw',
                    'outputs': [],
                    'type': 'function',
                },
                {
                    'constant': True,
                    'inputs': [
                        {
                            'name': '',
                            'type': 'address',
                        },
                    ],
                    'name': 'balanceOf',
                    'outputs': [
                        {
                            'name': '',
                            'type': 'uint256',
                        },
                    ],
                    'type': 'function',
                },
                {
                    'constant': False,
                    'inputs': [],
                    'name': 'deposit',
                    'outputs': [],
                    'type': 'function',
                },
            ],
            'code': '0x60606040526101b7806100126000396000f360606040526000357c0100000000000000000000000000000000000000000000000000000000900480632e1a7d4d1461004f57806370a0823114610067578063d0e30db0146100935761004d565b005b61006560048080359060200190919050506100a2565b005b61007d600480803590602001909190505061015c565b6040518082815260200191505060405180910390f35b6100a06004805050610177565b005b80600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505410156100de57610002565b80600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505403925050819055503373ffffffffffffffffffffffffffffffffffffffff168160405180905060006040518083038185876185025a03f192505050151561015857610002565b5b50565b60006000506020528060005260406000206000915090505481565b6001600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b56',
            'code_runtime': '0x60606040526000357c0100000000000000000000000000000000000000000000000000000000900480632e1a7d4d1461004f57806370a0823114610067578063d0e30db0146100935761004d565b005b61006560048080359060200190919050506100a2565b005b61007d600480803590602001909190505061015c565b6040518082815260200191505060405180910390f35b6100a06004805050610177565b005b80600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505410156100de57610002565b80600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505403925050819055503373ffffffffffffffffffffffffffffffffffffffff168160405180905060006040518083038185876185025a03f192505050151561015857610002565b5b50565b60006000506020528060005260406000206000915090505481565b6001600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b56',
            'meta': {
                'compilerVersion': '0.3.5-9da08ac3',
                'language': 'Solidity',
                'languageVersion': '0',
            },
            'source': None,
        },
    }
