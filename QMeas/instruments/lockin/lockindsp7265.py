from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265
from ..instrument import InstrumentDriver


class Driver(DSP7265, InstrumentDriver):
    """This class implements the Lock-in DSP7265 driver"""
    METHOD = ['Voltage', 'Frequency', 'Current', 'Phase']

    def __init__(self, visa_address):
        super().__init__(visa_address)
        self.CONTROL = {
            'Voltage': self.voltage,
            'Frequency': self.frequency,
            'Current': self.mag,
            'Phase': self.phase
        }

    def perform_open(self):
        pass

    def perform_close(self):
        self.shutdown()

    def perform_set_value(self, option, value, sweepRate=0.0):
        self.CONTROL[option] = value
        return value

    def perform_get_value(self, option, magnification):
        value = self.CONTROL[option]
        if option == 'Phase':
            value -= 0.63
        return value * magnification


if __name__ == '__main__':
    test = Driver("GPIB::6")
