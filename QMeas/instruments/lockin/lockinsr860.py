from qcodes.instrument_drivers.stanford_research.SR860 import SR860
from ..instrument import InstrumentDriver
from time import sleep


class Driver(InstrumentDriver):
    """ This class implements the Lock-in SR860 driver"""
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)', 'Magnitude(X)',
              'Phase', 'Analog in 1', 'Analog in 2', 'DC']

    def __init__(self, visa_address):
        self.sr860 = SR860("lockin", visa_address)
        self.CONTROL = {
            'Voltage': self.sr860.amplitude,
            'Frequency': self.sr860.frequency,
            'Magnitude(R)': self.sr860.R,
            'Magnitude(X)': self.sr860.X,
            'Phase': self.sr860.phase,
            'Analog in 1': self.sr860.aux_in0,
            'Analog in 2': self.sr860.aux_in1,
            'DC': self.sr860.sine_outdc
        }

    def perform_open(self):
        pass

    def perform_close(self):
        self.sr860.close()

    def perform_set_value(self, option, value, sweepRate=0.0):
        self.CONTROL[option](value)
        return value

    def perform_get_value(self, option, magnification):
        value = self.CONTROL[option]()
        return value * magnification
