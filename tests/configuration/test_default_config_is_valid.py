from populus import Project


def test_default_configuration_is_valid(project_dir):
    project = Project(create_config_file=True)
    assert project._project_config_schema is not None
    project.config.validate()
