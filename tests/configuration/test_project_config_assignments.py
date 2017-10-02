import pytest

from populus.config.defaults import (
    load_default_config,
)

from populus.config.base import (
    Config,
)


def test_user_config_not_assignable(project):
    with pytest.raises(AttributeError):
        project.user_config = Config()


def test_project_config_not_assignable(project):
    with pytest.raises(AttributeError):
        project.project_config = Config()


@pytest.mark.parametrize(
    'assigned_config',
    (
        load_default_config(),
        Config(load_default_config()),
    )
)
def test_config_assignment(project, user_config_defaults, assigned_config):
    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    default_value = user_config_defaults[changed_key]

    if isinstance(assigned_config, dict):
        assigned_config['compilation']['import_remappings'] = new_value
    else:
        assigned_config[changed_key] = new_value

    project.config = assigned_config

    assert project.user_config.get(changed_key) == default_value
    assert project.project_config.get(changed_key) == default_value
    assert project.config[changed_key] == new_value

    project.reload_config()

    assert project.config[changed_key] == default_value


def test_user_config_key_assignment(project, user_config_defaults):
    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    default_value = user_config_defaults[changed_key]

    project.user_config[changed_key] = new_value

    assert project.user_config.get(changed_key) == new_value
    assert project.project_config.get(changed_key) == default_value
    assert project.config.get(changed_key) == default_value

    project.reload_config()

    assert project.user_config.get(changed_key) == default_value


def test_project_config_key_assignment(project, user_config_defaults):

    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    default_value = user_config_defaults[changed_key]

    project.project_config[changed_key] = new_value

    assert project.user_config.get(changed_key) == default_value
    assert project.project_config.get(changed_key) == new_value
    assert project.config.get(changed_key) == default_value

    project.reload_config()

    assert project.project_config.get(changed_key) == default_value


def test_config_key_assignment(project, user_config_defaults):

    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    default_value = user_config_defaults[changed_key]

    project.config[changed_key] = new_value

    assert project.user_config.get(changed_key) == default_value
    assert project.project_config.get(changed_key) == default_value
    assert project.config.get(changed_key) == new_value

    project.reload_config()

    assert project.config.get(changed_key) == default_value
