import copy

from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade.v2 import (
    upgrade_v2_to_v3,
)
from populus.config.versions import (
    V3,
)

from populus.utils.mappings import (
    deep_merge_dicts,
)


V3_DEFAULT_CONFIG = load_default_config(version=V3)


BASE_V2_CONFIG = {
    "version": "2",
    "chains": {
        "mainnet": {
            "chain": {
                "class": "populus.chain.geth.MainnetChain"
            },
            "web3": {
                "$ref": "web3.GethIPC"
            },
            "contracts": {
                "backends": {
                    "JSONFile": {
                        "$ref": "contracts.backends.JSONFile"
                    },
                    "ProjectContracts": {
                        "$ref": "contracts.backends.ProjectContracts"
                    },
                    "Memory": {
                        "$ref": "contracts.backends.Memory"
                    }
                }
            }
        },
        "ropsten": {
            "chain": {
                "class": "populus.chain.geth.TestnetChain"
            },
            "web3": {
                "$ref": "web3.Ropsten"  # modified
            },
            "contracts": {
                "backends": {
                    "JSONFile": {
                        "$ref": "contracts.backends.JSONFile"
                    },
                    "ProjectContracts": {
                        "$ref": "contracts.backends.ProjectContracts"
                    },
                    "Memory": {
                        "$ref": "contracts.backends.Memory"
                    }
                }
            }
        },
        "temp": {
            "chain": {
                "class": "populus.chain.geth.TemporaryGethChain"
            },
            "web3": {
                "$ref": "web3.GethIPC"
            },
            "contracts": {
                "backends": {
                    "ProjectContracts": {
                        "$ref": "contracts.backends.ProjectContracts"
                    },
                    "Memory": {
                        "$ref": "contracts.backends.Memory"
                    }
                }
            }
        },
        "tester": {
            "chain": {
                "class": "populus.chain.tester.TesterChain"
            },
            "web3": {
                "$ref": "web3.Tester"
            },
            "contracts": {
                "backends": {
                    "ProjectContracts": {
                        "$ref": "contracts.backends.ProjectContracts"
                    },
                    "Memory": {
                        "$ref": "contracts.backends.Memory"
                    }
                }
            }
        },
        "testrpc": {
            "chain": {
                "class": "populus.chain.testrpc.TestRPCChain"
            },
            "web3": {
                "$ref": "web3.TestRPC"
            },
            "contracts": {
                "backends": {
                    "ProjectContracts": {
                        "$ref": "contracts.backends.ProjectContracts"
                    },
                    "Memory": {
                        "$ref": "contracts.backends.Memory"
                    }
                }
            }
        }
    },
    "contracts": {
        "backends": {
            "JSONFile": {
                "class": "populus.contracts.backends.filesystem.JSONFileBackend",
                "priority": 10,
                "settings": {
                    "file_path": "./registrar.json"
                }
            },
            "ProjectContracts": {
                "class": "populus.contracts.backends.project.ProjectContractsBackend",
                "priority": 20
            },
            "Memory": {
                "class": "populus.contracts.backends.memory.MemoryBackend",
                "priority": 50
            }
        }
    },
    "compilation": {
        "contracts_source_dir": "./path/to/my/contracts",  # custom
        "settings": {
            "optimize": True
        }
    },
    "web3": {
        "GethIPC": {
            "provider": {
                "class": "web3.providers.ipc.IPCProvider"
            }
        },
        "Ropsten": {   # custom
            "provider": {
                "class": "web3.providers.ipc.IPCProvider",
                "settings": {
                    "ipc_path": "/path/to/geth.ipc"
                }
            },
            "eth": {
                "default_account": "0xd3cda913deb6f67967b99d67acdfa1712c293601"
            }
        },
        "InfuraMainnet": {
            "eth": {
                "default_account": "0xd3cda913deb6f67967b99d67acdfa1712c293601"  # custom
            },
            "provider": {
                "class": "web3.providers.rpc.HTTPProvider",
                "settings": {
                    "endpoint_uri": "https://mainnet.infura.io"
                }
            }
        },
        "InfuraRopsten": {
            "eth": {
                "default_account": "0x0000000000000000000000000000000000000001"
            },
            "provider": {
                "class": "web3.providers.rpc.HTTPProvider",
                "settings": {
                    "endpoint_uri": "https://ropsten.infura.io"
                }
            }
        },
        "TestRPC": {
            "provider": {
                "class": "web3.providers.tester.TestRPCProvider"
            }
        },
        "Tester": {
            "provider": {
                "class": "web3.providers.tester.EthereumTesterProvider"
            }
        }
    }
}


EXPECTED_V3_CONFIG = deep_merge_dicts(
    V3_DEFAULT_CONFIG,
    {'web3': {'Ropsten': BASE_V2_CONFIG['web3']['Ropsten']}},
    {'web3': {'InfuraMainnet': {'eth': BASE_V2_CONFIG['web3']['InfuraMainnet']['eth']}}},
    {'compilation': {'contracts_source_dir': BASE_V2_CONFIG['compilation']['contracts_source_dir']}},  # noqa: E501
    {'chains': {'ropsten': {'web3': BASE_V2_CONFIG['chains']['ropsten']['web3']}}},
)


def test_non_default_v2_config_upgrade():
    v2_config = copy.deepcopy(BASE_V2_CONFIG)
    copy.deepcopy(V3_DEFAULT_CONFIG)

    upgraded_config = upgrade_v2_to_v3(v2_config)
    assert upgraded_config == EXPECTED_V3_CONFIG
