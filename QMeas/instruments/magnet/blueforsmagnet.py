"""Module Bluefors AMI magnet

Progress:
    Successfully query the magnet through the visa address:
        TCPIP0::192.168.50.61::7180::SOCKET

Todo:
    * VISA address
    the address is not shown in the visa list. the user has to
    add it or type the address manually.

    * Run error
    The script seems to have a bug when the user run the whole
    script. The solution is to run it separately as two parts:
    1st part: from first line to the mark
    2nd part: after the mark
"""
from time import sleep
import pyvisa as visa
from .magnet import Magnet


class Driver(Magnet):
    """Class Bluefors AMI magnet"""

    def __init__(self):
        super().__init__()
        rm = visa.ResourceManager()
        self.magnet = rm.open_resource('TCPIP0::192.168.50.66::7180::SOCKET')
        self.magnet.read_termination = '\r\n'

        # remove hello word
        for _ in range(2):
            self.magnet.write('FIELD:MAGnet?')
            self.magnet.read()
        # Pause mode
        self.magnet.write('PAUSE')
        sleep(0.1)

    def perform_open(self):
        pass

    def perform_close(self):
        command = 'PAUSE'
        self.magnet.write(command)
        sleep(0.1)
        self.magnet.close()

    def set_magnetic(self, value: float) -> float:
        self.magnet.write(f'CONFigure:FIELD:TARGet {value}') # set target
        self.magnet.write('RAMP') # ramp mode

    def get_magnetic(self):
        value = float(self.magnet.query('FIELD:MAGnet?'))
        return value
