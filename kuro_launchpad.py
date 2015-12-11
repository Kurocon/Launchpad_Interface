from logging.config import fileConfig, logging
import pypm
from handlers.multi_page_handler import MultiPageHandler

__author__ = 'kevin'

from settings import *

def find_launchpad():

    launch_in = -1
    launch_out = -1

    for loop in range(pypm.CountDevices()):
        interf, name, inp, outp, opened = pypm.GetDeviceInfo(loop)
        if "Launchpad" in name:
            if inp:
                print "Found Launchpad Input at {}:{}".format(interf, loop)
                launch_in = loop
            if outp:
                print "Found Launchpad Output at {}:{}".format(interf, loop)
                launch_out = loop

        if launch_in != -1 and launch_out != -1:
            return launch_in, launch_out

def open_launchpad(dev_in, dev_out):
    launch_in = pypm.Input(dev_in)
    launch_out = pypm.Output(dev_out, 0)

    return launch_in, launch_out

if __name__ == '__main__':
    fileConfig('logging_config.conf')
    log = logging.getLogger(__name__)
    log.debug("Debugging mode enabled...")

    log.info("KuroLaunchpad starting...")

    # Handler initialisation
    h = MultiPageHandler()

    # Initialize Interface
    if use_debug_gui:
        log.info("Using the Debug GUI to emulate a Launchpad")
        from interfaces.gui_interface import GuiInterface
        i = GuiInterface(h)
        i.start()

    else:
        log.info("Using a MIDI connection to a real Launchpad")
        from interfaces.launchpad_interface import LaunchpadInterface
        # Initialize LP
        i = LaunchpadInterface(h)
        i.start()
