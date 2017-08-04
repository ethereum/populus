
from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.compile import (
    write_compiled_sources,
)

from populus.project import (
    Project
)


def compile(project_root_dir):

    project = Project(project_root_dir)
    _, compiled_contracts = compile_project_contracts(project)
    write_compiled_sources(project.compiled_contracts_asset_path, compiled_contracts)
