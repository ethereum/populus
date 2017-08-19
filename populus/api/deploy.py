import os

from populus.project import (
    Project,
)

from populus.contracts.provider import (
    Provider,
)

from populus.contracts.registrar import (
    Registrar,
)

from populus.contracts.helpers import (
    get_provider_backends,
    get_registrar_backends,
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

    chain = get_chain(chain_name, user_config, chain_dir=project.project_root_dir)
    web3 = chain.web3
    contract_backends = chain.contract_backends

    registrar_backends = get_registrar_backends(contract_backends)
    if not registrar_backends:
        raise ValueError(
            "Must have at least one registrar backend for chain {chain_name}".format(
                chain_name=chain_name
            )
        )

    provider_backends = get_provider_backends(contract_backends)
    if not provider_backends:
        raise ValueError(
            "Must have at least one provider backend for chain {chain_name}".format(
                chain_name=chain_name
            )
        )

    registrar = Registrar(web3, registrar_backends, base_dir=project_root_dir)
    provider = Provider(web3, registrar, provider_backends, project)






