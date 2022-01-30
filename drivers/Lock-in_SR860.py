from utils import DriverInterface
from qcodes.instrument_drivers.stanford_research.SR860 import SR860
from time import sleep


class Driver(DriverInterface):
    METHOD = ['Voltage', 'Frequency',
              'Magnitude(R)', 'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2', 'DC']

    def __init__(self, visa_address):
        self.sr860 = SR860("lockin", visa_address)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.sr860.close()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'Voltage':
            self.sr860.amplitude(value)
        elif option == 'Frequency':
            self.sr860.frequency(value)
        elif option == 'Magnitude(R)':
            self.sr860.R(value)
        elif option == 'Magnitude(X)':
            self.sr860.X(value)
        elif option == 'Phase':
            self.sr860.phase(value)
        elif option == 'Analog in 1':
            self.sr860.aux_in0(value)
        elif option == 'Analog in 2':
            self.sr860.aux_in1(value)
        elif option == 'DC':
            self.sr860.sine_outdc(value)
        return value

    def performGetValue(self, option, magnification):
        """Perform the Get Value instrument operation"""
        if option == 'Voltage':
            value = self.sr860.amplitude()
        elif option == 'Frequency':
            value = self.sr860.frequency()
        elif option == 'Magnitude(R)':
            value = self.sr860.R()
        elif option == 'Magnitude(X)':
            value = self.sr860.X()
        elif option == 'Phase':
            value = self.sr860.phase()
        elif option == 'Analog in 1':
            value = self.sr860.aux_in0()
        elif option == 'Analog in 2':
            value = self.sr860.aux_in1()
        elif option == 'DC':
            value = self.sr860.sine_outdc()
        return value * magnification


if __name__ == '__main__':
    pass
