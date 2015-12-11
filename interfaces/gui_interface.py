import time

__author__ = 'kevin'

import Tkinter

from threading import Thread
from interfaces.generic_interface import Interface

from util.utils import get_button_id

import logging

"""
An interface to use a GUI as an in/output device.
"""
class GuiInterface(Interface):
    def __init__(self, handler):
        Interface.__init__(self)

        self.log = logging.getLogger(__name__)

        # Setup handler
        self.log.debug("Setting up handler...")
        handler.set_interface(self)

        # Setup sender
        self.log.debug("Setting up sender...")
        GuiSender.interface = self
        self.sender = GuiSender.get_instance()

        # Setup listener
        self.log.debug("Setting up listener...")
        GuiListener.msg_handler = handler
        GuiListener.interface = self
        self.listener = GuiListener.get_instance()

    def start(self):
        self.log.debug("Starting GuiInterface...")
        self.listener.start()

"""
A listener for the GuiInterface.
The variables GuiListener.top, GuiListener.msg_handler and GuiListener.interface
need to be set before instantiating the class with GuiListener.get_instance()
"""
class GuiListener(Thread):
    _instance = None
    msg_handler = None
    interface = None
    top = None

    def __init__(self, msg_handler, top):
        """
        Initializes a GuiListener
        :param msg_handler: A Handler-subclass to handle the GUI presses
        :param top: The tkinter root element
        """
        super(GuiListener, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.info("GuiListener {} starting...".format(self.name))
        self.top = top
        self.msg_handler = msg_handler
        self.started = False
        self.needs_to_run = False
        self.buttons = [[], [], [], [], [], [], [], []]
        self.control_buttons = []
        self.side_buttons = []

    def button_pressed(self, fx, fy):
        self.log.debug("Button {},{} pressed".format(fx, fy))
        btn_id = get_button_id(fx, fy)

        # Construct btn-on object
        data = [[[144, btn_id, 127, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)
        # Wait a bit
        time.sleep(0.2)
        # Construct btn-off object
        data = [[[144, btn_id, 0, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)

    def controlbutton_pressed(self, num):
        self.log.debug("Control button {} pressed".format(num))

        # Construct btn-on object
        data = [[[176, (104+num), 127, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)
        # Wait a bit
        time.sleep(0.2)
        # Construct btn-off object
        data = [[[176, (104+num), 0, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)

    def sidebutton_pressed(self, num):
        self.log.debug("Side button {} pressed".format(num))

        btn_id = [8, 24, 40, 56, 72, 88, 104, 120][num]

        # Construct btn-on object
        data = [[[144, btn_id, 127, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)
        # Wait a bit
        time.sleep(0.2)
        # Construct btn-off object
        data = [[[144, btn_id, 0, 0], [0]]]
        # Pass on to handler
        self.msg_handler.handle_message(data)

    def run(self):
        """
        Starts the listener-thread
        """
        self.needs_to_run = True
        self.started = True
        self.log.debug("GuiListener {} running.".format(self.name))

        self.log.debug("Initializing GuiInterface...")
        top = Tkinter.Tk()
        top.title("LaunchPad Debug GUI")

        self.log.debug("Adding buttons...")

        toprow_text = ["^", "v", "<", ">", "SE", "U1", "U2", "MX"]

        for x in range(0, 8):
            for y in range(0, 8):
                b = Tkinter.Button(top, height=3, width=6, command=lambda nx=x, ny=y: self.button_pressed(nx, ny))
                b.grid(column=x, row=y+1)
                self.buttons[x].append(b)

        for z in range(0, 8):
            c = Tkinter.Button(top, height=3, width=6, text=toprow_text[z], command=lambda nz=z: self.controlbutton_pressed(nz))
            d = Tkinter.Button(top, height=3, width=6, text=">", command=lambda nz=z: self.sidebutton_pressed(nz))
            c.grid(column=z, row=0)
            d.grid(column=8, row=z+1)
            self.control_buttons.append(c)
            self.side_buttons.append(d)

        self.interface.top = top
        self.interface.sender.top = top
        self.top = top

        # Prepare the LP layout
        self.log.debug("Preparing the Launchpad Layout")
        self.msg_handler.prepare()

        self.top.mainloop()

    def stop(self):
        """
        Stops the listener thread.
        """
        self.log.info("GuiListener {} stopping...".format(self.name))
        self.needs_to_run = False
        self.started = False

    @classmethod
    def get_instance(cls):
        """
        Get the current GuiListener instance
        :return: A GuiListener instance
        """
        if not cls._instance:
            cls._instance = GuiListener(GuiListener.msg_handler, GuiListener.top)
        return cls._instance

"""
Sender for the GuiInterface to send data to the GUI
"""
class GuiSender:
    top = None
    interface = None
    _instance = None

    def __init__(self, top):
        self.top = top

    def send(self, x, y, color):
        """
        Sends a message to a specific button on the GUI.
        :param x: The x-value of the button (0-based)
        :param y: The y-value of the button (0-based)
        :param color: The color as a string. You can use one of the util.gui_colors colors for this.
        """

        if y == -1:
            # Control row
            self.interface.listener.control_buttons[x].configure(bg=color)
        else:
            if x == 8:
                # Side buttons
                self.interface.listener.side_buttons[y].configure(bg=color)
            else:
                # Normal button
                self.interface.listener.buttons[x][y].configure(bg=color)

    @classmethod
    def get_instance(cls):
        """
        Get the current GuiSender instance
        :return: A GuiSender instance
        """
        if not cls._instance:
            cls._instance = GuiSender(GuiSender.top)

        return cls._instance
