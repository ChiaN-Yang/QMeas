from pymeasure.instruments.srs.sr830 import SR830
from ..instrument import InstrumentDriver
from time import sleep


class Driver(SR830, InstrumentDriver):
    """ This class implements the Lock-in SR830 driver"""
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)', 'Magnitude(X)', 'Phase', 'Analog in 1',
              'Analog in 2', 'Magnitude(R) with auto sensitivity',
              'Magnitude(X) with auto sensitivity', 'Triton Temperature (AUX in 3)']
    SCALE_RANGE_LEFT = 0.2
    SCALE_RANGE_RIGHT = 0.8
    ADJUST_SCALE_TIME = 1.5

    def __init__(self, visa_address):
        SR830.__init__(self, visa_address)
        self.auto_sensitivity = False
        self.CONTROL = {
            'Voltage': self.sine_voltage,
            'Frequency': self.frequency,
            'Magnitude(R)': self.magnitude,
            'Magnitude(X)': self.x,
            'Phase': self.theta,
            'Analog in 1': self.aux_in_1,
            'Analog in 2': self.aux_in_2,
        }

    def perform_open(self):
        self.pos = self.SENSITIVITIES.index(self.sensitivity)
        self.first_run = True

    def perform_close(self):
        self.shutdown()

    def perform_set_value(self, option, value, sweepRate=0.0):
        self.CONTROL[option] = value
        if option == 'Voltage':
            return self.perform_get_value(option, 1)
        return value

    def perform_get_value(self, option, magnification):
        if option == 'Triton Temperature (AUX in 3)':
            return self.get_triton_temperature(magnification)
        if self.auto_sensitivity:
            self.adjust_sensitivity()
        value = float(self.CONTROL[option]) * magnification
        return value

    def get_triton_temperature(self, magnification):
        if self.first_run:
            # voltage setting in Lakeshore
            volt_low = -10
            volt_high = 10
            # user-defined two temperature endpoints (K)
            # magnification = '50,125'; scale = ['50','125']
            scale = str(magnification).split(',')
            endpoint_1 = float(scale[0])  # temp in [K] for -10V
            endpoint_2 = float(scale[1])  # temp in [K] for +10V
            if endpoint_1 > endpoint_2:
                endpoint_1, endpoint_2 = endpoint_2, endpoint_1
            # Calculate the slope and intercept
            self.slope = (endpoint_2 - endpoint_1) / (volt_high - volt_low)
            self.intercept = self.slope * (-volt_high) + endpoint_2
            self.first_run = False
        # Calculate the corresponding Temperature
        aux_volt = self.aux_in_3
        value = round(aux_volt*self.slope + self.intercept, 7)
        return value

    def adjust_sensitivity(self):
        """Set voltage scale to current range"""
        if self.input_config == 'I (1 MOhm)':
            vi_factor = 1e-6
        else:
            vi_factor = 1
        percent = self.magnitude / (self.sensitivity*vi_factor)

        # Auto range
        if percent < self.SCALE_RANGE_LEFT:
            self.sensitivity = self.SENSITIVITIES[self.pos - 1]
            self.pos = self.SENSITIVITIES.index(self.sensitivity)
            sleep(self.ADJUST_SCALE_TIME)
        elif percent > self.SCALE_RANGE_RIGHT:
            self.sensitivity = self.SENSITIVITIES[self.pos + 1]
            self.pos = self.SENSITIVITIES.index(self.sensitivity)
            sleep(self.ADJUST_SCALE_TIME)
