from libs.driver_interface import DriverInterface
from pymeasure.instruments.srs.sr830 import SR830


class Driver(SR830, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)',
              'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2']

    def __init__(self, visa_address):
        SR830.__init__(self, visa_address)

    def performOpen(self, option):
        """Perform the operation of opening the instrument connection"""
        # Resets the instrument and clears the queue
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.shutdown()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'Voltage':
            self.sine_voltage = value
        elif option == 'Frequency':
            self.frequency = value
        elif option == 'Magnitude(R)':
            self.magnitude = value
        elif option == 'Magnitude(X)':
            self.x = value
        elif option == 'Phase':
            self.theta = value
        elif option == 'Analog in 1':
            self.aux_in_1 = value
        elif option == 'Analog in 2':
            self.aux_in_2 = value
        return self.performGetValue(option)

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        if option == 'Voltage':
            return self.sine_voltage
        elif option == 'Frequency':
            return self.frequency
        elif option == 'Magnitude(R)':
            return self.magnitude
        elif option == 'Magnitude(X)':
            return self.x
        elif option == 'Phase':
            return self.theta
        elif option == 'Analog in 1':
            return self.aux_in_1
        elif option == 'Analog in 2':
            return self.aux_in_2


if __name__ == '__main__':
    pass
