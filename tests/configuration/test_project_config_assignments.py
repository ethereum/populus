import pytest

from populus.config.defaults import (
    load_default_config,
    load_user_default_config,
)

from populus.config.base import (
    Config,
)


def test_user_config_not_assignable(project):
    user_config = load_user_default_config()
    with pytest.raises(AttributeError):
        project.user_config = user_config


@pytest.mark.parametrize(
    'assigned_config',
    (
        load_default_config(),
        Config(load_default_config()),
    )
)
def test_project_config_assignment(project, user_config_defaults, assigned_config):

    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    if isinstance(assigned_config, dict):
        assigned_config['compilation']['import_remappings'] = new_value
    else:
        assigned_config[changed_key] = new_value

    project.project_config = assigned_config

    assert project.user_config.get(changed_key) == user_config_defaults[changed_key]
    assert project.project_config.get(changed_key) == new_value
    merged_config = project.merge_user_and_project_configs(
        project.user_config,
        project.project_config
    )
    assert merged_config[changed_key] == new_value
    assert project.config[changed_key] == new_value


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
    if isinstance(assigned_config, dict):
        assigned_config['compilation']['import_remappings'] = new_value
    else:
        assigned_config[changed_key] = new_value

    project.config = assigned_config

    assert project.user_config.get(changed_key) == user_config_defaults[changed_key]
    assert project.project_config.get(changed_key) == new_value
    merged_config = project.merge_user_and_project_configs(
        project.user_config,
        project.project_config
    )
    assert merged_config[changed_key] == new_value
    assert project.config[changed_key] == new_value


def test_user_config_key_assignment(project, user_config_defaults):

    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']

    project.user_config[changed_key] = new_value

    assert project.user_config.get(changed_key) == new_value
    assert project.project_config.get(changed_key) == user_config_defaults[changed_key]
    assert project.config.get(changed_key) == user_config_defaults[changed_key]

    merged_config = project.merge_user_and_project_configs(
        project.user_config,
        project.project_config
    )
    assert merged_config[changed_key] == user_config_defaults[changed_key]


def test_project_config_key_assignment(project, user_config_defaults):

    changed_key = 'compilation.import_remappings'
    new_value = ['new-ramappings=contracts']
    new_value2 = ['new-ramappings2=contracts']

    project.project_config[changed_key] = new_value

    assert project.user_config.get(changed_key) == user_config_defaults[changed_key]
    assert project.project_config.get(changed_key) == new_value
    merged_config = project.merge_user_and_project_configs(
        project.user_config,
        project.project_config
    )
    assert merged_config[changed_key] == new_value
    assert project.config.get(changed_key) == new_value

    # correct caching
    project.project_config[changed_key] = new_value2

    assert project.user_config.get(changed_key) == user_config_defaults[changed_key]
    assert project.project_config.get(changed_key) == new_value2
    merged_config = project.merge_user_and_project_configs(
        project.user_config,
        project.project_config
    )
    assert merged_config[changed_key] == new_value2
    assert project.config.get(changed_key) == new_value2
