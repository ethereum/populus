

from populus.config.chain import (
    ChainConfig,
)


def get_chain_config(chain_name, user_config):

    chain_config_key = 'chains.{chain_name}'.format(chain_name=chain_name)

    if chain_config_key in user_config:
        return user_config.get_config(chain_config_key, config_class=ChainConfig)
    else:
        raise KeyError(
                "Unknown chain: {0!r} - Must be one of {1!r}".format(
                    chain_name,
                    sorted(user_config.get('chains', {}).keys()),
                )
            )


def get_chain(chain_name, user_config):
    """
    Returns a context manager that runs a chain within the context of the
    current populus project.

    Alternatively you can specify any chain name that is present in the
    `chains` configuration key.
    """

    chain_config = get_chain_config(chain_name, user_config)
    chain = chain_config.chain_class(chain_name, chain_config, user_config)
    return chain