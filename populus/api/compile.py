
from populus.project import (
    Project,
)

from populus.compilation.compile import (
     compile_dirs,
)

from populus.compilation.helpers import (
    write_compiled_sources,
)

from .config import (
    load_global_config,
)

def compile(project_root_dir,global_config_path):

    project = Project(project_root_dir)

    _, compiled_contracts = compile_dirs(
        (project.contracts_source_dir,project.tests_dir,),
        global_config=load_global_config(global_config_path),
        import_remappings=project.config.get('compilation.import_remappings')
    )

    write_compiled_sources(project.compiled_contracts_asset_path, compiled_contracts)

    return project



