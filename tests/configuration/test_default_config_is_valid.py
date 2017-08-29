from populus import Project


def test_default_configuration_is_valid(project):

    assert project._project_config_schema is not None
    project.config.validate()
