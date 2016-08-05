from populus.migrations import (
    RunPython,
)


def test_run_python_operation(web3):
    target = []

    def execute(web3, **kwargs):
        target.append('it-ran')


    run_python_operation = RunPython(execute)
    run_python_operation.execute(web3=web3)

    assert len(target) == 1
    assert target[0] == 'it-ran'
