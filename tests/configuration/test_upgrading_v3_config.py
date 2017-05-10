import pytest

import copy

from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade.v3 import (
    upgrade_v3_to_v4,
)
from populus.config.versions import (
    V3,
    V4,
)

from populus.utils.mappings import (
    deep_merge_dicts,
)


V4_DEFAULT_CONFIG = load_default_config(version=V4)


BASE_V3_CONFIG = {
  "version": "3",
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
          "Memory": {
            "$ref": "contracts.backends.Memory"
          },
          "ProjectContracts": {
            "$ref": "contracts.backends.ProjectContracts"
          },
          "TestContracts": {
            "$ref": "contracts.backends.TestContracts"
          }
        }
      }
    },
    "ropsten": {
      "chain": {
        "class": "populus.chain.geth.TestnetChain"
      },
      "web3": {
        "$ref": "web3.GethIPC"
      },
      "contracts": {
        "backends": {
          "JSONFile": {
            "$ref": "contracts.backends.JSONFile"
          },
          "Memory": {
            "$ref": "contracts.backends.Memory"
          },
          "ProjectContracts": {
            "$ref": "contracts.backends.ProjectContracts"
          },
          "TestContracts": {
            "$ref": "contracts.backends.TestContracts"
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
          "Memory": {
            "$ref": "contracts.backends.Memory"
          },
          "ProjectContracts": {
            "$ref": "contracts.backends.ProjectContracts"
          },
          "TestContracts": {
            "$ref": "contracts.backends.TestContracts"
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
          "Memory": {
            "$ref": "contracts.backends.Memory"
          },
          "ProjectContracts": {
            "$ref": "contracts.backends.ProjectContracts"
          },
          "TestContracts": {
            "$ref": "contracts.backends.TestContracts"
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
          "Memory": {
            "$ref": "contracts.backends.Memory"
          },
          "ProjectContracts": {
            "$ref": "contracts.backends.ProjectContracts"
          },
          "TestContracts": {
            "$ref": "contracts.backends.TestContracts"
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
      "TestContracts": {
        "class": "populus.contracts.backends.testing.TestContractsBackend",
        "priority": 40
      },
      "Memory": {
        "class": "populus.contracts.backends.memory.MemoryBackend",
        "priority": 50
      }
    }
  },
  "compilation": {
    "contracts_source_dir": "./contracts",
    "settings": {
      "optimize": True,
      "optimize_runs": 201  # custom
    }
  },
  "web3": {
    "GethIPC": {
      "provider": {
        "class": "web3.providers.ipc.IPCProvider"
      }
    },
    "InfuraMainnet": {
      "eth": {
        "default_account": "0x0000000000000000000000000000000000000001"
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


EXPECTED_V4_CONFIG = deep_merge_dicts(
    V4_DEFAULT_CONFIG,
    {'compilation': {'backends': {'SolcCombinedJSON': {'settings': {
        'optimize': True,
        'optimize_runs': 201,
    }}}}},
)


def test_non_default_v3_config_upgrade():
    v3_config = copy.deepcopy(BASE_V3_CONFIG)
    v4_default_config = copy.deepcopy(V4_DEFAULT_CONFIG)

    upgraded_config = upgrade_v3_to_v4(v3_config)
    assert upgraded_config == EXPECTED_V4_CONFIG
