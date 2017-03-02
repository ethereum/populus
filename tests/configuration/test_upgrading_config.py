import copy
import json

from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade import (
    upgrade_v1_to_v2,
)

from populus.utils.config import (
    get_json_config_file_path,
)
from populus.utils.mappings import (
    deep_merge_dicts,
)


def test_default_config_upgrade():
    v1_default_config = load_default_config(version='1')
    v2_default_config = load_default_config(version='2')

    upgraded_v1_config = upgrade_v1_to_v2(v1_default_config)
    assert upgraded_v1_config == v2_default_config


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
      "eth": {  # custom
        "default_account": "0xd3cda913deb6f67967b99d67acdfa1712c293601"
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


def test_non_default_config_upgrade():
    v1_config = copy.deepcopy(BASE_V1_CONFIG)
    v2_default_config = load_default_config(version='2')
    expected_v2_config = deep_merge_dicts(
        v2_default_config,
        {'web3': {'Ropsten': v1_config['web3']['Ropsten']}},
        {'web3': {'InfuraMainnet': {'eth': v1_config['web3']['InfuraMainnet']['eth']}}},
        {'compilation': {'contracts_source_dir': v1_config['compilation']['contracts_dir']}},
        {'chains': {'ropsten': {'web3': v1_config['chains']['ropsten']['web3']}}},
    )


    upgraded_config = upgrade_v1_to_v2(v1_config)
    assert upgraded_config == expected_v2_config


def test_upgrade_works_with_config_objects(project):
    config_file_path = get_json_config_file_path(project.project_dir)
    with open(config_file_path, 'w') as config_file:
        json.dump(BASE_V1_CONFIG, config_file)
    project.load_config()
    assert 'web3.Ropsten' in project.config
    upgraded_config = upgrade_v1_to_v2(project.config)

    expected_v2_config = deep_merge_dicts(
        v2_default_config,
        {'web3': {'Ropsten': v1_config['web3']['Ropsten']}},
        {'web3': {'InfuraMainnet': {'eth': v1_config['web3']['InfuraMainnet']['eth']}}},
        {'compilation': {'contracts_source_dir': v1_config['compilation']['contracts_dir']}},
        {'chains': {'ropsten': {'web3': v1_config['chains']['ropsten']['web3']}}},
    )
    assert upgraded_config == expected_v2_config
