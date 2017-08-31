from .config import (
    load_user_config
)


from populus.project import (
    Project,
)


from populus.compilation.compile_contracts import (
     compile_dirs,
)

from populus.compilation.helpers import (
    write_compiled_sources,
)


def compile_project_dir(project_root_dir, user_config_path=None):

    user_config = load_user_config(user_config_path)
    project = Project(project_root_dir, user_config)
    import_remmapings = user_config.import_remmapings(project)

    # TODO don't compile with a project property so global path is provided once
    _, compiled_contracts = compile_dirs(
        (project.contracts_source_dir, project.tests_dir,),
        user_config,
        import_remmapings
    )

    write_compiled_sources(project.compiled_contracts_asset_path, compiled_contracts)

    return project
