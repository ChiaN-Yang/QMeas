from libs.driver_interface import DriverInterface
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265


class Driver(DSP7265, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Current', 'Phase']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self, option):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        pass

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        pass


if __name__ == '__main__':
    pass
