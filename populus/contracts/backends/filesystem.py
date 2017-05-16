from __future__ import absolute_import

import json
import os

from eth_utils import (
    to_tuple,
)

from populus.contracts.exceptions import (
    NoKnownAddress,
)

from populus.utils.mappings import (
    set_nested_key,
)
from populus.utils.chains import (
    get_chain_definition,
    check_if_chain_matches_chain_uri,
)
from populus.utils.contract_key_mapping import (
    ContractKeyMapping,
    ContractKeyMappingEncoder,
)

from .base import (
    BaseContractBackend,
)


@to_tuple
def get_matching_chain_definitions(web3, values):
    for chain_definition in values:
        if check_if_chain_matches_chain_uri(web3, chain_definition):
            yield chain_definition


def load_registrar_data(registrar_file):
    registrar_data = json.load(registrar_file)
    registrar_data.setdefault('deployments', {})

    for chain_definition, raw_map in registrar_data['deployments'].items():
        registrar_data['deployments'][chain_definition] = ContractKeyMapping.from_dict(raw_map)

    return registrar_data


class JSONFileBackend(BaseContractBackend):
    is_registrar = True
    is_provider = False

    #
    # Registrar API
    #
    def set_contract_address(self, instance_identifier, address):
        registrar_data = self.registrar_data

        chain_definition = get_chain_definition(self.chain.web3)
        set_nested_key(
            registrar_data,
            'deployments.{0}.{1}'.format(chain_definition, instance_identifier),
            address,
            mapping_type=ContractKeyMapping,
        )

        with open(self.registrar_path, 'w') as registrar_file:
            json.dump(
                registrar_data,
                registrar_file,
                sort_keys=True,
                indent=2,
                separators=(',', ': '),
                cls=ContractKeyMappingEncoder
            )

    @to_tuple
    def get_contract_addresses(self, instance_identifier):
        registrar_data = self.registrar_data
        matching_chain_definitions = get_matching_chain_definitions(
            self.chain.web3,
            registrar_data.get('deployments', {}),
        )

        identifier_exists = any(
            instance_identifier in registrar_data['deployments'][chain_definition]
            for chain_definition
            in matching_chain_definitions
        )
        if not identifier_exists:
            raise NoKnownAddress("No known address for '{0}'".format(instance_identifier))

        for chain_definition in matching_chain_definitions:
            chain_deployments = registrar_data['deployments'][chain_definition]
            if instance_identifier in chain_deployments:
                yield chain_deployments[instance_identifier]

    #
    # Private API
    #
    @property
    def registrar_path(self):
        return self.config.get('file_path', './registrar.json')

    @property
    def registrar_data(self):
        # TODO: this could be cached using mtime of the file.
        if os.path.exists(self.registrar_path):
            with open(self.registrar_path, 'r') as registrar_file:
                registrar_data = load_registrar_data(registrar_file)
        else:
            registrar_data = {'deployments':{}}

        return registrar_data
