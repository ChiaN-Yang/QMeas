from libs.driver_interface import DriverInterface
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265


class Driver(DSP7265, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Current', 'Phase']

    def __init__(self, VISA, name, type):
        super().__init__(VISA)
        self.Ins_name = name
        self.Ins_type = type
        self.Ins_VISA_add = VISA

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, value, options={}, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        pass

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        pass


if __name__ == '__main__':
    pass
