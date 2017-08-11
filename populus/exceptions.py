class PopulusException(Exception):
    pass


class ValidationError(PopulusException):
    pass


class ConfigError(PopulusException):
    pass
