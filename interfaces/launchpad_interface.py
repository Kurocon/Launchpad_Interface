from threading import Thread
import sys
from interfaces.generic_interface import Interface

import logging
import pypm

__author__ = 'kevin'

"""
An interface to use the Launchpad as an in/output device.
"""
class LaunchpadInterface(Interface):

    _instance = None
    handler = None

    def __init__(self, handler):
        Interface.__init__(self)
        self.log = logging.getLogger(__name__)

        # Initialize Launchpad
        self.log.info("Searching for launchpad...")
        pypm.Initialize()
        dev_in, dev_out = LaunchpadInterface.find_launchpad()

        # Check if we found the LP
        if dev_in == -1 or dev_out == -1:
            self.log.error("Could not find the LaunchPad. Did you connect it?")
            sys.exit(1)

        # Setup the connection
        self.midi_in = pypm.Input(dev_in)
        self.midi_out = pypm.Output(dev_out, 0)

        # Switch to index-based layout
        self.midi_out.Write([[[0xB0, 0x00, 0x01], pypm.Time()]])

        # Reset the launchpad
        self.midi_out.Write([[[0xB0, 0x00, 0x00], pypm.Time()]])

        # Setup handler
        self.log.debug("Setting up handler...")
        handler.set_interface(self)

        # Setup sender
        LaunchpadSender.midi_out = self.midi_out
        self.sender = LaunchpadSender.get_instance()

        # Setup listener
        LaunchpadListener.midi_in = self.midi_in
        LaunchpadListener.msg_handler = handler
        LaunchpadListener.interface = self
        self.listener = LaunchpadListener.get_instance()

        self.log.info("Connected to Launchpad and ready to start.")

    def start(self):
        self.log.debug("Starting LaunchpadInterface...")
        self.listener.start()

    @staticmethod
    def find_launchpad():
        launch_in = -1
        launch_out = -1

        log = logging.getLogger(__name__)

        for loop in range(pypm.CountDevices()):
            interf, name, inp, outp, opened = pypm.GetDeviceInfo(loop)
            if "Launchpad" in name:
                if inp:
                    log.info("Found Launchpad Input at {}:{}".format(interf, loop))
                    launch_in = loop
                if outp:
                    log.info("Found Launchpad Output at {}:{}".format(interf, loop))
                    launch_out = loop

            if launch_in != -1 and launch_out != -1:
                return launch_in, launch_out

        return -1, -1

    @classmethod
    def get_instance(cls):
        """
        Get the current LaunchpadInterface instance
        :return: A LaunchpadInterface instance
        """
        if not cls._instance:
            cls._instance = LaunchpadInterface(LaunchpadInterface.handler)
        return cls._instance

"""
A listener for the LaunchpadInterface.
The variables LaunchpadListener.midi_in, LaunchpadListener.msg_handler and LaunchpadListener.interface
need to be set before instantiating the class with LaunchpadListener.get_instance()
"""
class LaunchpadListener(Thread):
    _instance = None
    midi_in = None
    msg_handler = None
    interface = None

    def __init__(self, midi_in, msg_handler):
        """
        Initializes a LaunchpadListener
        :param midi_in: The midi-in interface used for the launchpad
        :param msg_handler: A Handler-subclass to handle the launchpad's midi-messages
        """
        super(LaunchpadListener, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.info("LaunchpadListener {} starting...".format(self.name))
        self.midi_in = midi_in
        self.msg_handler = msg_handler
        self.started = False
        self.needs_to_run = False

    def run(self):
        """
        Starts the listener-thread
        """
        self.needs_to_run = True
        self.started = True

        # Prepare the LP layout
        self.log.debug("Preparing the Launchpad Layout")
        self.msg_handler.prepare()

        self.log.debug("LaunchpadListener {} running.".format(self.name))

        while self.needs_to_run:
            while not self.midi_in.Poll() and self.needs_to_run:
                pass  # Wait for new message
            data = self.midi_in.Read(1)  # Read one message

            self.log.debug("Message received. Calling handler.")
            self.msg_handler.handle_message(data)

    def stop(self):
        """
        Stops the listener thread.
        """
        self.log.info("LaunchpadListener {} stopping...".format(self.name))
        self.needs_to_run = False
        self.started = False

    @classmethod
    def get_instance(cls):
        """
        Get the current LaunchpadListener instance
        :return: A LaunchpadListener instance
        """
        if not cls._instance:
            cls._instance = LaunchpadListener(LaunchpadListener.midi_in, LaunchpadListener.msg_handler)
        return cls._instance

"""
Sender for the LaunchpadInterface to send data to the Launchpad
"""
class LaunchpadSender:
    midi_out = None
    _instance = None

    def __init__(self, midi_out):
        self.midi_out = midi_out
        self.log = logging.getLogger(__name__)

    def send(self, x, y, color):
        """
        Sends a message to a specific button on the LaunchPad.
        :param x: The x-value of the button (0-based)
        :param y: The y-value of the button (0-based)
        :param color: The color in hexadecimal. You can use one of the util.colors colors for this.
        """
        if self.midi_out:
            self.midi_out.Write([[[0x90, (y * 16) + x, color], pypm.Time()]])
        else:
            self.log.error("Could not write to the Launchpad")

    @classmethod
    def get_instance(cls):
        """
        Get the current LaunchpadSender instance
        :return: A LaunchpadSender instance
        """
        if not cls._instance:
            cls._instance = LaunchpadSender(LaunchpadSender.midi_out)

        return cls._instance
