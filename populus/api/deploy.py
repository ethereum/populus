import os

from populus.project import (
    Project,
)

from populus.utils.cli import (
    select_chain,
    deploy_contract_and_verify,
    select_project_contract,
)

from populus.config.loading import (
    load_deploy_config,
    load_user_config,
)

from populus.chain.helpers import (
    get_chain,
    get_chain_config,
)


def deploy(project_root_dir, user_config_path, chain_name):

    user_config = load_user_config(user_config_path)
    project = Project(project_root_dir, user_config)
    contract_data = project.compiled_contract_data

    if os.path.exists(project.deploy_config_path):
        deploy_config = load_deploy_config(project.deploy_config_path)
        contracts_to_deploy = deploy_config.get("contracts")
    else:
        contracts_to_deploy = contract_data.keys()

    with get_chain(chain_name, user_config, chain_dir=project.project_root_dir) as chain:
        provider = chain.provider
        registrar = chain.registrar






