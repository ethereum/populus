from populus.compilation import (
    compile_project_contracts,
    post_process_compiled_sources,
)


def test_library_code_is_linked():
    contracts = compile_project_contracts('./projects/test-01/')
    processed_contracts = post_process_compiled_sources(contracts)

    assert False
    x = 3
