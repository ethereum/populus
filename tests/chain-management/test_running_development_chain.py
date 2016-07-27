from populus.chain import (
    dev_geth_process,
)


def test_running_development_chain(project_dir):
    with dev_geth_process(project_dir, 'development') as geth:
        # TODO: what to assert here?
        assert geth.is_alive
