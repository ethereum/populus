class BaseCompilerBackend(object):
    compiler_settings = None

    def __init__(self, settings):
        self.compiler_settings = settings

    def get_compiled_contract_data(self, source_file_paths, import_remappings):
        raise NotImplementedError("Must be implemented by subclasses")
