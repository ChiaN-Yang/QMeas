from libs.driver_interface import DriverInterface
from pymeasure.instruments.keithley import Keithley2400


class Driver(Keithley2400, DriverInterface):
    METHOD = ['Current', 'Voltage']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self, option):
        """Perform the operation of opening the instrument connection"""
        # Enables the front terminals for measurement, and disables the rear terminals.
        self.use_front_terminals

        if self.option == 'Current':
            # Configures the instrument to apply a source current
            self.apply_current()
            # Enables the source of voltage depending on the configuration of the instrument.
            self.enable_source()
        elif self.option == 'Voltage':
            # Configures the instrument to apply a source current
            self.apply_voltage()
            # Enables the source of voltage depending on the configuration of the instrument.
            self.enable_source()

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.shutdown()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if self.option == 'Current':
            # output current
            self.source_current = value
        elif self.option == 'Voltage':
            # output voltage
            self.source_voltage = value

        return value

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        self.sample_continuously()
        if self.option == 'Current':
            value = self.measure_current()
        elif self.option == 'Voltage':
            value = self.measure_voltage()

        return value


if __name__ == '__main__':
    a = Driver('GPIB:1', 'K2400', 'Keithley2400')
    a.performOpen
