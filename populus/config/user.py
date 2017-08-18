from .base import Config


class UserConfig(Config):

    def __init__(self, config, parent=None, schema=None):

        super(UserConfig, self).__init__(config, parent, schema)

