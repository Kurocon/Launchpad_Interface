__author__ = 'kevin'

class CommunicationsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
