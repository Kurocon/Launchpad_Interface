import logging

from handlers.generic_handler import Handler
from util.utils import get_button_xy

__author__ = 'kevin'


class SinglePageHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.log = logging.getLogger(__name__)
        self.interface = None

    def set_interface(self, interface):
        self.interface = interface

    def handle_message(self, data):
        msg_type = data[0][0][0]
        button = data[0][0][1]
        value = data[0][0][2]

        if msg_type == 144:  # Button Triggered
            x, y = get_button_xy(button)

            if value == 0:
                self.handle_button_off(x, y)
            elif value == 127:
                self.handle_button_on(x, y)
            else:
                self.log.debug("Button {},{} - {}".format(y, x, value))
        else:
            self.log.debug("Received message at time {}".format(data[0][1]))
            self.log.debug("{} {} {} {}".format(data[0][0][0], data[0][0][1], data[0][0][2], data[0][0][3]))

    def prepare(self):
        pass

    def handle_button_on(self, x, y):
        pass

    def handle_button_off(self, x, y):
        pass
