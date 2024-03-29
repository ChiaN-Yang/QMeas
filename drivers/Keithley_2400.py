from utils import DriverInterface
from pymeasure.instruments.keithley import Keithley2400
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class Driver(Keithley2400, DriverInterface):
    METHOD = ['Current', 'Current with Auto-range', 'Voltage']

    current_auto_range = Instrument.control(
        ":SENS:CURR:RANG:AUTO?",":SENS:CURR:RANG:AUTO %d",
        """ A integer property that switches the measurement current
        range to Auto-range, which can take values between 1 or 0.
        """,
        validator=strict_discrete_set,
        values=[0,1],
        cast=int )

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
        # First run helps to switch the Auto-range function
        self.first_run = True

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.stop_buffer()
        self.local_switch()

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

    def performGetValue(self, option, magnification):
        """Perform the Get Value instrument operation"""
        if option == 'Current':
            value = float(self.current[1]) * magnification
        elif option == 'Current with Auto-range':
            # enable the Auto-range function
            if self.first_run:
                self.current_auto_range = 1
                self.first_run = False
            value = float(self.current[1]) * magnification
        elif option == 'Voltage':
            value = float(self.voltage[0]) * magnification
        return value

    def local_switch(self):
        """ Disables remote mode and switch the system to local mode"""
        self.write(":SYSTEM:LOCAL")


if __name__ == '__main__':
    a = Driver('GPIB:24', 'K2400', 'Keithley2400')
    a.performOpen
