from populus.chain.helpers import (
    get_chain,
)

from populus.api.config import (
    write_user_config,
)

def test_chain_web3_is_preconfigured_with_default_from(project, user_config, user_config_path):
    default_account = '0x0000000000000000000000000000000000001234'
    user_config['web3.Tester.eth.default_account'] = default_account
    write_user_config(user_config, user_config_path)

    with get_chain('tester', user_config, chain_dir=project.project_root_dir) as chain:
        web3 = chain.web3

        assert web3.eth.defaultAccount == default_account
        assert web3.eth.coinbase != default_account
