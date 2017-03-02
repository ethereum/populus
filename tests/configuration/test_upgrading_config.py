import pytest

import copy
import json

from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade import (
    upgrade_config,
)
from populus.config.upgrade.v1 import (
    upgrade_v1_to_v2,
)
from populus.config.versions import (
    V1,
    V2,
)

from populus.utils.config import (
    get_json_config_file_path,
)
from populus.utils.mappings import (
    deep_merge_dicts,
)


V1_DEFAULT_CONFIG = load_default_config(version=V1)
V2_DEFAULT_CONFIG = load_default_config(version=V2)


@pytest.mark.parametrize(
    'upgrade_fn,upgrade_args',
    (
        (upgrade_v1_to_v2, tuple()),
        (upgrade_config, (V2,)),
    )
)
def test_default_config_upgrade(upgrade_fn, upgrade_args):
    v1_default_config = copy.deepcopy(V1_DEFAULT_CONFIG)
    v2_default_config = copy.deepcopy(V2_DEFAULT_CONFIG)

    upgraded_v1_config = upgrade_fn(v1_default_config, *upgrade_args)
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

EXPECTED_V2_CONFIG = deep_merge_dicts(
    V2_DEFAULT_CONFIG,
    {'web3': {'Ropsten': BASE_V1_CONFIG['web3']['Ropsten']}},
    {'web3': {'InfuraMainnet': {'eth': BASE_V1_CONFIG['web3']['InfuraMainnet']['eth']}}},
    {'compilation': {'contracts_source_dir': BASE_V1_CONFIG['compilation']['contracts_dir']}},
    {'chains': {'ropsten': {'web3': BASE_V1_CONFIG['chains']['ropsten']['web3']}}},
)


@pytest.mark.parametrize(
    'upgrade_fn,upgrade_args',
    (
        (upgrade_v1_to_v2, tuple()),
        (upgrade_config, (V2,)),
    )
)
def test_non_default_config_upgrade(upgrade_fn, upgrade_args):
    v1_config = copy.deepcopy(BASE_V1_CONFIG)
    v2_default_config = copy.deepcopy(V2_DEFAULT_CONFIG)

    upgraded_config = upgrade_fn(v1_config, *upgrade_args)
    assert upgraded_config == EXPECTED_V2_CONFIG


@pytest.mark.parametrize(
    'upgrade_fn,upgrade_args',
    (
        (upgrade_v1_to_v2, tuple()),
        (upgrade_config, (V2,)),
    )
)
def test_upgrade_works_with_config_objects(project, upgrade_fn, upgrade_args):
    v1_config = copy.deepcopy(BASE_V1_CONFIG)

    config_file_path = get_json_config_file_path(project.project_dir)
    with open(config_file_path, 'w') as config_file:
        json.dump(v1_config, config_file)
    project.load_config()
    assert 'web3.Ropsten' in project.config

    upgraded_config = upgrade_fn(v1_config, *upgrade_args)

    assert upgraded_config == EXPECTED_V2_CONFIG
