class Empty(object):
    pass


#
# This is a singleton object to differentiate between `None` being passed in as
# an argument and an argument not being specified.
#
empty = Empty()
