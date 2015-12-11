import logging

__author__ = 'kevin'

class Handler:

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def handle_message(self, data):
        self.log.debug("MESSAGE: {}".format(data))
