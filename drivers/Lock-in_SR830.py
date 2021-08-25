from libs.driver_interface import DriverInterface
from pymeasure.instruments.srs.sr830 import SR830


class Driver(SR830, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)',
              'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2']

    def __init__(self, VISA, name, type):
        super().__init__(VISA)
        self.Ins_name = name
        self.Ins_type = type
        self.Ins_VISA_add = VISA

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # Resets the instrument and clears the queue
        pass

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        self.shutdown()

    def performSetValue(self, value, options={}, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if options == 'Voltage':
            self.sine_voltage = value
        elif options == 'Frequency':
            self.frequency = value
        elif options == 'Magnitude(R)':
            self.magnitude = value
        elif options == 'Magnitude(X)':
            self.x = value
        elif options == 'Phase':
            self.theta = value
        elif options == 'Analog in 1':
            self.aux_in_1 = value
        elif options == 'Analog in 2':
            self.aux_in_2 = value
        return value

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        if options == 'Voltage':
            return self.sine_voltage
        elif options == 'Frequency':
            return self.frequency
        elif options == 'Magnitude(R)':
            return self.magnitude
        elif options == 'Magnitude(X)':
            return self.x
        elif options == 'Phase':
            return self.theta
        elif options == 'Analog in 1':
            return self.aux_in_1
        elif options == 'Analog in 2':
            return self.aux_in_2


if __name__ == '__main__':
    pass
