import itertools

from .base import Config


class UserConfig(Config):

    def __init__(self, config, parent=None, schema=None):

        super(UserConfig, self).__init__(config, parent, schema)

    def import_remmapings(self, project):

        return tuple(
            itertools.chain(
                self.get("compilation.import_remappings", []),
                project.config.get('compilation.import_remappings', [])
            )
        )
