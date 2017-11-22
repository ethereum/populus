from .base import (
    BaseCompilerBackend,
)


class ViperBackend(BaseCompilerBackend):
    project_source_extensions = ('*.v.py', '*.vy')
    test_source_extensions = ('*.py', )
