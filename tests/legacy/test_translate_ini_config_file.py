from populus.legacy.config import translate_legacy_ini_config_file


CONFIG_A = """[populus]
project_dir=/home/ubuntu/my-project
contracts_dir=/home/ubuntu/my-project/some-custom-contracts-dir
"""


def test_simple_config_file(project_dir, write_project_file):
    write_project_file('populus.ini', CONFIG_A)
    upgraded_config = translate_legacy_ini_config_file('populus.ini')
    assert upgraded_config == {
        'populus': {
            'project_dir': '/home/ubuntu/my-project',
        },
        'compilation': {
            'contracts_dir': '/home/ubuntu/my-project/some-custom-contracts-dir',
        }
    }


CONFIG_B = """[populus]
project_dir=/home/ubuntu/my-project
contracts_dir=/home/ubuntu/my-project/some-custom-contracts-dir

[chain:custom-chain]
"""


def test_config_with_custom_chain_in_chains(project_dir, write_project_file):
    write_project_file('populus.ini', CONFIG_B)
    upgraded_config = translate_legacy_ini_config_file('populus.ini')
    assert upgraded_config == {
        'populus': {
            'project_dir': '/home/ubuntu/my-project',
        },
        'compilation': {
            'contracts_dir': '/home/ubuntu/my-project/some-custom-contracts-dir',
        },
        'chains': {
            'custom-chain': {
                'chain': {
                    'class': 'populus.chain.LocalGethChain',
                },
                'web3': {
                    'provider': {
                        'class': 'web3.providers.ipc.IPCProvider',
                    }
                }
            },
        }
    }


CONFIG_C = """[populus]
project_dir=/home/ubuntu/my-project
contracts_dir=/home/ubuntu/my-project/some-custom-contracts-dir

[chain:ropsten]
"""


def test_config_with_named_chain_in_chains(project_dir, write_project_file):
    write_project_file('populus.ini', CONFIG_C)
    upgraded_config = translate_legacy_ini_config_file('populus.ini')
    assert upgraded_config == {
        'populus': {
            'project_dir': '/home/ubuntu/my-project',
        },
        'compilation': {
            'contracts_dir': '/home/ubuntu/my-project/some-custom-contracts-dir',
        },
        'chains': {
            'ropsten': {
                'chain': {
                    'class': 'populus.chain.TestnetChain',
                },
                'web3': {
                    'provider': {
                        'class': 'web3.providers.ipc.IPCProvider',
                    }
                }
            },
        }
    }


CONFIG_D = """[populus]
project_dir=/home/ubuntu/my-project
contracts_dir=/home/ubuntu/my-project/some-custom-contracts-dir

[chain:ropsten]
provider=web3.providers.rpc.RPCProvider
"""


def test_config_with_rpc_provider_chains(project_dir, write_project_file):
    write_project_file('populus.ini', CONFIG_D)
    upgraded_config = translate_legacy_ini_config_file('populus.ini')
    assert upgraded_config == {
        'populus': {
            'project_dir': '/home/ubuntu/my-project',
        },
        'compilation': {
            'contracts_dir': '/home/ubuntu/my-project/some-custom-contracts-dir',
        },
        'chains': {
            'ropsten': {
                'chain': {
                    'class': 'populus.chain.TestnetChain',
                },
                'web3': {
                    'provider': {
                        'class': 'web3.providers.rpc.HTTPProvider',
                        'settings': {
                            'endpoint_uri': "http://localhost:8545",
                        }
                    }
                }
            },
        }
    }


CONFIG_E = """[populus]
project_dir=/home/ubuntu/my-project
contracts_dir=/home/ubuntu/my-project/some-custom-contracts-dir

[chain:mainnet]
provider=web3.providers.rpc.RPCProvider
rpc_port=8546
"""


def test_config_with_rpc_settings_chains(project_dir, write_project_file):
    write_project_file('populus.ini', CONFIG_E)
    upgraded_config = translate_legacy_ini_config_file('populus.ini')
    assert upgraded_config == {
        'populus': {
            'project_dir': '/home/ubuntu/my-project',
        },
        'compilation': {
            'contracts_dir': '/home/ubuntu/my-project/some-custom-contracts-dir',
        },
        'chains': {
            'mainnet': {
                'chain': {
                    'class': 'populus.chain.MainnetChain',
                },
                'web3': {
                    'provider': {
                        'class': 'web3.providers.rpc.HTTPProvider',
                        'settings': {
                            'endpoint_uri': "http://localhost:8546",
                        }
                    }
                }
            },
        }
    }
