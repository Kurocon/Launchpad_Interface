import logging

from handlers.generic_handler import Handler

from util.buttons import *

__author__ = 'kevin'


class MultiPageHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.log = logging.getLogger(__name__)
        self.interface = None
        self.pages = []
        self.current_page = 0

    def set_interface(self, interface):
        self.interface = interface
        for page in self.pages:
            page.set_interface(interface)

        self.log.debug("Set the interface in MultiPageHandler")

    def prepare(self):
        self.log.debug("Preparing page {}".format(self.current_page+1))
        self.pages[self.current_page].prepare()

    def handle_message(self, data):
        msg_type = data[0][0][0]
        button = data[0][0][1]
        value = data[0][0][2]

        # Control button (top) triggered
        if msg_type == 176:
            if value == 127:
                if button == TOP_LEFT:
                    # Switch to previous page
                    self.previous_page()
                elif button == TOP_RIGHT:
                    # Switch to next page
                    self.next_page()
                else:
                    self.log.debug("Control message {}: {}".format(button, value))
            else:
                self.log.debug("Control message {}: {}".format(button, value))
        else:
            # Call current page handler
            self.pages[self.current_page].handle_message(data)

    def previous_page(self):
        # Decrement page number
        self.current_page = ((self.current_page-1) % len(self.pages))

        self.log.debug("Switching to previous page ({})".format(self.current_page+1))

        # Initialize page
        self.prepare()

    def next_page(self):
        # Increment page number
        self.current_page = ((self.current_page+1) % len(self.pages))

        self.log.debug("Switching to next page ({})".format(self.current_page+1))

        # Initialize page
        self.prepare()

    def add_page(self, page_handler):
        if self.interface:
            page_handler.set_interface(self.interface)

        self.pages.append(page_handler)

        self.log.debug("New page added. Now {} registered pages".format(len(self.pages)))
