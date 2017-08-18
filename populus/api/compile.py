from populus.config.loading import (
    load_user_config
)


from populus.project import (
    Project,
)


from populus.compilation.compile import (
     compile_dirs,
)

from populus.compilation.helpers import (
    write_compiled_sources,
)


def compile(project_root_dir, user_config_path):

    user_config = load_user_config(user_config_path)
    project = Project(project_root_dir, user_config)

    #TODO don't compile with a project property so global path is provided once
    _, compiled_contracts = compile_dirs(
        (project.contracts_source_dir, project.tests_dir,),
        user_config,
        project.config.get('compilation.import_remappings')
    )

    write_compiled_sources(project.compiled_contracts_asset_path, compiled_contracts)

    return project



