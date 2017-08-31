import logging
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
    deploy_contract_and_verify,
)

from populus.utils.compat import (
    sleep,
)

from populus.utils.deploy import (
    get_deploy_order,
)

from populus.config.loading import (
    load_deploy_config,
)

from .config import (
    load_user_config,
)

from populus.chain.helpers import (
    get_chain,
    is_synced,
)


def deploy(project_root_dir, chain_name, user_config_path=None, wait_for_sync=True, logger=None):

    if logger is None:
        logger = logging.getLogger('populus.deploy')

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

    # wait for the chain to start syncing.
    if wait_for_sync:
        logger.info("Waiting for chain to start syncing....")
        while chain.wait.for_syncing() and is_synced(chain.web3):
            sleep(1)
        logger.info("Chain sync complete")

    # Get the deploy order.
    deploy_order = get_deploy_order(
            contracts_to_deploy,
            project.compiled_contract_data,
        )

    # Display Start Message Info.
    starting_msg = (
            "Beginning contract deployment.  Deploying {0} total contracts ({1} "
            "Specified, {2} because of library dependencies)."
            "\n\n" +
            (" > ".join(deploy_order))
            ).format(
            len(deploy_order),
            len(contracts_to_deploy),
            len(deploy_order) - len(contracts_to_deploy),
        )
    logger.info(starting_msg)

    for contract_name in deploy_order:
        if not provider.are_contract_dependencies_available(contract_name):
            raise ValueError(
                    "Something is wrong with the deploy order.  Some "
                    "dependencies for {0} are not "
                    "available.".format(contract_name)
                )

        # Check if we already have an existing deployed version of that
        # contract (via the registry).  For each of these, prompt the user
        # if they would like to use the existing version.
        if provider.is_contract_available(contract_name):
            existing_contract_instance = provider.get_contract(contract_name)
            found_existing_contract_msg = (
                    "Found existing version of {name} in registrar. "
                    "Would you like to use the previously deployed "
                    "contract @ {address}?".format(
                        name=contract_name,
                        address=existing_contract_instance.address,
                    )
                )
            logger.info(found_existing_contract_msg)

        # We don't have an existing version of this contract available so
        # deploy it.
        contract_instance = deploy_contract_and_verify(
                chain,
                provider,
                contract_name=contract_name,
            )

        # Store the contract address for linking of subsequent deployed contracts.
        registrar.set_contract_address(contract_name, contract_instance.address)

    success_msg = (
            "Deployment Successful."
        )
    logger.info(success_msg)
