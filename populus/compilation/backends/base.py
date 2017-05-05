class BaseCompilerBackend(object):
    project = None
    config = None

    def __init__(self, project, config):
        self.project = project
        self.config = config

    def get_compiler_output(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def get_normalized_compiler_output(self, compiler_output):
        raise NotImplementedError("Must be implemented by subclasses")
