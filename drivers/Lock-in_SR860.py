from utils import DriverInterface
from qcodes.instrument_drivers.stanford_research.SR860 import SR860
from time import sleep


class Driver(SR860, DriverInterface):
    METHOD = ['Voltage', 'Frequency',
              'Magnitude(R)', 'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2', 'DC']

    def __init__(self, visa_address):
        SR860.__init__(self, "lockin", visa_address)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.close()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'Voltage':
            self.amplitude(value)
        elif option == 'Frequency':
            self.frequency(value)
        elif option == 'Magnitude(R)':
            self.R(value)
        elif option == 'Magnitude(X)':
            self.X(value)
        elif option == 'Phase':
            self.phase(value)
        elif option == 'Analog in 1':
            self.aux_in0(value)
        elif option == 'Analog in 2':
            self.aux_in1(value)
        elif option == 'DC':
            self.sine_outdc(value)
        return value

    def performGetValue(self, option, magnification):
        """Perform the Get Value instrument operation"""
        if option == 'Voltage':
            value = self.amplitude()
        elif option == 'Frequency':
            value = self.frequency()
        elif option == 'Magnitude(R)':
            value = self.R()
        elif option == 'Magnitude(X)':
            value = self.X()
        elif option == 'Phase':
            value = self.phase()
        elif option == 'Analog in 1':
            value = self.aux_in0()
        elif option == 'Analog in 2':
            value = self.aux_in1()
        elif option == 'DC':
            value = self.sine_outdc()
        return value * magnification


if __name__ == '__main__':
    pass
