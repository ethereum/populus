from eth_utils import (
    to_ordered_dict,
)


@to_ordered_dict
def get_registrar_backends(contract_backends):

    for backend_name, backend in contract_backends.items():
        if backend.is_registrar:
            yield backend_name, backend


@to_ordered_dict
def get_provider_backends(contract_backends):

    for backend_name, backend in contract_backends.items():
        if backend.is_provider:
            yield backend_name, backend