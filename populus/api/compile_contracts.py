import threading

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.cli import (
    watch_project_contracts,
)
from populus.utils.compile import (
    write_compiled_sources,
)


def compile_project(project, watch):

    _, compiled_contracts = compile_project_contracts(project)
    write_compiled_sources(project.compiled_contracts_asset_path, compiled_contracts)

    if watch:
        thread = threading.Thread(
            target=watch_project_contracts,
            kwargs={'project': project},
        )
        thread.daemon = True
        thread.start()
        thread.join()
