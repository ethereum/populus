import pytest

import copy

from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade.v1 import (
    upgrade_v1_to_v2,
)
from populus.config.versions import (
    V1,
    V2,
)

from populus.utils.mappings import (
    deep_merge_dicts,
)


V1_DEFAULT_CONFIG = load_default_config(version=V1)
V2_DEFAULT_CONFIG = load_default_config(version=V2)


BASE_V1_CONFIG = {
  "version": "1",
  "chains": {
    "mainnet": {
      "chain": {
        "class": "populus.chain.MainnetChain"
      },
      "web3": {
        "$ref": "web3.GethIPC"
      }
    },
    "ropsten": {
      "chain": {
        "class": "populus.chain.TestnetChain"
      },
      "web3": {
        "$ref": "web3.Ropsten"  # modified
      }
    },
    "temp": {
      "chain": {
        "class": "populus.chain.TemporaryGethChain"
      },
      "web3": {
        "$ref": "web3.GethIPC"
      }
    },
    "tester": {
      "chain": {
        "class": "populus.chain.TesterChain"
      },
      "web3": {
        "$ref": "web3.Tester"
      }
    },
    "testrpc": {
      "chain": {
        "class": "populus.chain.TestRPCChain"
      },
      "web3": {
        "$ref": "web3.TestRPC"
      }
    }
  },
  "compilation": {
    "contracts_dir": "./path/to/my/contracts",  # custom
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

EXPECTED_V2_CONFIG = deep_merge_dicts(
    V2_DEFAULT_CONFIG,
    {'web3': {'Ropsten': BASE_V1_CONFIG['web3']['Ropsten']}},
    {'web3': {'InfuraMainnet': {'eth': BASE_V1_CONFIG['web3']['InfuraMainnet']['eth']}}},
    {'compilation': {'contracts_source_dir': BASE_V1_CONFIG['compilation']['contracts_dir']}},
    {'chains': {'ropsten': {'web3': BASE_V1_CONFIG['chains']['ropsten']['web3']}}},
)


def test_non_default_v1_config_upgrade():
    v1_config = copy.deepcopy(BASE_V1_CONFIG)
    v2_default_config = copy.deepcopy(V2_DEFAULT_CONFIG)

    upgraded_config = upgrade_v1_to_v2(v1_config)
    assert upgraded_config == EXPECTED_V2_CONFIG
