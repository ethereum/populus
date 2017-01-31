import os

import anyconfig

from populus.utils.functional import (
    cached_property,
)
from populus.utils.chains import (
    is_BIP122_block_uri,
    parse_BIP122_uri,
    get_chain_definition,
    check_if_chain_matches_chain_uri,
)

from .base import (
    BaseContractBackend,
)


class JSONFileBackend(BaseContractBackend):
    @property
    def is_provider(self):
        return self.settings.get('use_as_provider', True)

    @property
    def is_registrar(self):
        return self.settings.get('use_as_registrar', True)

    #
    # Registrar API
    #
    def set_contract_address(self, key, address):
        # TODO
        raise NotImplementedError("Must be implemented by subclasses")

    #
    # ProviderAPI
    #
    def get_contract_address(self, contract_identifier):
        assert False

    #
    # Private API
    #
    @cached_property
    def chain_definition(self):
        return get_chain_definition(self.chain.web3)

    @property
    def file_path(self):
        return self.config['path']

    def write_value_to_file(self, key, value):
        if os.path.exists(self.file_path):
            data = anyconfig.load(self.file_path)
        else:
            data = anyconfig.to_container({})

        web3 = self.chain.web3

        existing_chain_definitions = tuple(
            (key, parse_BIP122_uri(key))
            for key
            in data
            if is_BIP122_block_uri(key) and check_if_chain_matches_chain_uri(web3, key)
        )

        if not len(existing_chain_definitions):
            chain_definition = get_chain_definition(web3)
        elif len(existing_chain_definitions) == 1:
            chain_definition, _ = existing_chain_definitions[0]
        else:
            resolved_and_sorted_definitions = tuple(sorted(
                (web3.eth.getBlock(block_hash)['number'], value)
                for (value, (_, _, block_hash))
                in existing_chain_definitions
            ))
            _, chain_definition = resolved_and_sorted_definitions[-1]

            for duplicate_definition in resolved_and_sorted_definitions[:-1]:
                # eww. mutation
                data[chain_definition].update(
                    data.pop(duplicate_definition),
                    ac_merge=anyconfig.MS_NO_REPLACE,
                )

        update_values = anyconfig.to_container({
            chain_definition: {key: value},
        })

        data.update(update_values)
        anyconfig.dump(data, self.file_path)
