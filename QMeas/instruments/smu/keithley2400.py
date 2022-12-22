from ..instrument import InstrumentDriver
from pymeasure.instruments.keithley import Keithley2400
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class Keithley2400(Keithley2400, InstrumentDriver):
    METHOD = ['Current', 'Current with Auto-range', 'Voltage']

    current_auto_range = Instrument.control(
        ":SENS:CURR:RANG:AUTO?", ":SENS:CURR:RANG:AUTO %d",
        """ A integer property that switches the measurement current
        range to Auto-range, which can take values between 1 or 0.
        """,
        validator=strict_discrete_set,
        values=[0, 1],
        cast=int)

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def perform_open(self):
        # Enables the front terminals for measurement, and disables the rear terminals.
        self.use_front_terminals()
        self.sample_continuously()
        # First run helps to switch the Auto-range function
        self.first_run = True

    def perform_close(self):
        self.stop_buffer()
        self.local_switch()

    def perform_set_value(self, option, value, sweepRate=0.0):
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

    def perform_get_value(self, option, magnification):
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
