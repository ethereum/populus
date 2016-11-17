import pytest

from populus.utils.packaging import(
    is_valid_package_identifier,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        # Just Package Names
        ('populus', True),
        ('with-12345', True),
        ('with-dash', True),
        # Names with versions
        ('populus==1.0.0', True),
        ('populus>=1.0.0', True),
        ('populus<=1.0.0', True),
        ('populus>1.0.0', True),
        ('populus<1.0.0', True),
        # Names with versions and prerelease
        ('populus==1.0.0-beta1', True),
        ('populus==1.0.0-b1', True),
        ('populus==1.0.0-beta1.other2', True),
        ('populus==1.0.0-beta1.other2.another', True),
        # Names with versions and build
        ('populus==1.0.0+d4feab1', True),
        ('populus==1.0.0+d4feab1.deadbeef', True),
        # Names with versions and prerelease and build
        ('populus==1.0.0-beta1+d4feab1', True),
        ('populus==1.0.0-beta1.another2+d4feab1.deadbeef', True),
        # Bad Names
        ('-dash-start', False),
        ('0-number-start', False),
        ('with_underscore', False),
        ('withCapital', False),
    ),
)
def testis_valid_package_identifier(value, expected):
    actual = is_valid_package_identifier(value)
    assert actual is expected
