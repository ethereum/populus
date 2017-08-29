from .base import Config


class DeployConfig(Config):

    def __init__(self, config, parent=None, schema=None):

        super(DeployConfig,self).__init__(config,parent,schema)

