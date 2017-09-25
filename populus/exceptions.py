class PopulusException(Exception):
    pass


class PopulusResourceWarning(Warning):
    # replace with ResourceWarning when migrating to python 3
    pass


class ValidationError(PopulusException):
    pass
