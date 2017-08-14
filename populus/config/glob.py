from .base import Config


class GlobalConfig(Config):

    def __init__(self, config, parent=None, schema=None):

        super(GlobalConfig,self).__init__(config,parent,schema)

