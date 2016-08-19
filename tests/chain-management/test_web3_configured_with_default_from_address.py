from geth.accounts import create_new_account

from web3.utils.string import force_text

from populus.project import Project


def test_chain_web3_is_preconfigured_with_default_from(project_dir,
                                                       write_project_file):
    write_project_file('populus.ini', '[chain:local]')

    project = Project()

    chain = project.get_chain('local')

    default_account = force_text(
        create_new_account(chain.geth.data_dir, b'a-test-password')
    )

    project.config.set('chain:local', 'default_account', default_account)
    project.write_config()

    with chain:
        web3 = chain.web3

        assert len(web3.eth.accounts) == 2
        assert web3.eth.defaultAccount == default_account
        assert web3.eth.coinbase != default_account
