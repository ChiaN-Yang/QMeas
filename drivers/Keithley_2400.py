from libs.driver_interface import DriverInterface
from pymeasure.instruments.keithley import Keithley2400


class Driver(Keithley2400, DriverInterface):
    METHOD = ['Current', 'Voltage']

    def __init__(self, VISA, name, type):
        super().__init__(VISA)
        self.Ins_name = name
        self.Ins_type = type
        self.Ins_VISA_add = VISA

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # Enables the front terminals for measurement, and disables the rear terminals.
        self.use_front_terminals

        if options == 'Current':
            # Configures the instrument to apply a source current
            self.apply_current()
            # Enables the source of voltage depending on the configuration of the instrument.
            self.enable_source()
        elif options == 'Voltage':
            # Configures the instrument to apply a source current
            self.apply_voltage()
            # Enables the source of voltage depending on the configuration of the instrument.
            self.enable_source()

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        self.shutdown()

    def performSetValue(self, value, options={}, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if options == 'Current':
            # output current
            self.source_current = value
        elif options == 'Voltage':
            # output voltage
            self.source_voltage = value

        return value

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        self.sample_continuously()
        if options == 'Current':
            value = self.measure_current()
        elif options == 'Voltage':
            value = self.measure_voltage()

        return value


if __name__ == '__main__':
    a = Driver('K2400', 'Keithley2400', 26)
    a.performOpen
