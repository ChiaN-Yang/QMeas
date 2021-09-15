from libs.driver_interface import DriverInterface
from pymeasure.instruments.keithley import Keithley2400


class Driver(Keithley2400, DriverInterface):
    METHOD = ['Current', 'Voltage']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        # Resets the instrument and clears the queue
        # self.reset()
        # Enables the front terminals for measurement, and disables the rear terminals.
        self.use_front_terminals()
        self.sample_continuously()
        # Enables the source of voltage depending on the configuration of the instrument.
        # self.enable_source()

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.stop_buffer()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'Current':
            if self.source_mode != 'current':
                # Configures the instrument to apply a source current
                self.apply_current()
            # output current
            self.source_current = value
        elif option == 'Voltage':
            if self.source_mode != 'voltage':
                # Configures the instrument to apply a source current
                self.apply_voltage()
            # output voltage
            self.source_voltage = value

        return value

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        if option == 'Current':
            if not self.current:
                self.measure_current()
            value = self.current[0]
        elif option == 'Voltage':
            if not self.voltage:
                self.measure_voltage()
            value = self.voltage[0]

        return value


if __name__ == '__main__':
    a = Driver('GPIB:24', 'K2400', 'Keithley2400')
    a.performOpen
