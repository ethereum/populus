from populus.migrations import (
    RunPython,
)


def test_run_python_operation(web3, chain):
    target = []

    def execute(chain, **kwargs):
        target.append('it-ran')


    run_python_operation = RunPython(execute)
    run_python_operation.execute(chain=chain)

    assert len(target) == 1
    assert target[0] == 'it-ran'
