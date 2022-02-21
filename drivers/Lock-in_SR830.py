from utils import DriverInterface
from pymeasure.instruments.srs.sr830 import SR830
from time import sleep


class Driver(SR830, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)', 'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2',
              'Magnitude(R) with auto sensitivity', 'Magnitude(X) with auto sensitivity','Triton Temperature (AUX in 3)']

    def __init__(self, visa_address):
        SR830.__init__(self, visa_address)
        self.SCALE_RANGE_LEFT = 0.2
        self.SCALE_RANGE_RIGHT = 0.8
        self.ADJUST_SCALE_TIME = 1.5

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        self.pos = self.SENSITIVITIES.index(self.sensitivity)
        self.first_run = True

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.shutdown()

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'Voltage':
            self.sine_voltage = value
            return self.performGetValue(option, 1)
        elif option == 'Frequency':
            self.frequency = value
        elif option == 'Magnitude(R)' or option == 'Magnitude(R) with auto sensitivity':
            self.magnitude = value
        elif option == 'Magnitude(X)' or option == 'Magnitude(X) with auto sensitivity':
            self.x = value
        elif option == 'Phase':
            self.theta = value
        elif option == 'Analog in 1':
            self.aux_in_1 = value
        elif option == 'Analog in 2':
            self.aux_in_2 = value
        return value

    def performGetValue(self, option, magnification):
        """Perform the Get Value instrument operation"""
        if option == 'Voltage':
            value = self.sine_voltage
        elif option == 'Frequency':
            value = self.frequency
        elif option == 'Magnitude(R)':
            value = self.magnitude
        elif option == 'Magnitude(X)':
            value = self.x
        elif option == 'Phase':
            value = self.theta
        elif option == 'Analog in 1':
            value = self.aux_in_1
        elif option == 'Analog in 2':
            value = self.aux_in_2
        elif option == 'Magnitude(R) with auto sensitivity':
            self.autoSensitivity()
            value = self.magnitude
        elif option == 'Magnitude(X) with auto sensitivity':
            self.autoSensitivity()
            value = self.x
        elif option == 'Triton Temperature (AUX in 3)':
            if self.first_run:
                # voltage setting in Lakeshore
                volt_low = -10
                volt_high = 10
                # user-defined two temperature endpoints (K)
                # magnification = '50,125'; scale = ['50','125']
                scale = str(magnification).split(',')
                endpoint_1 = float(scale[0]) # temp in [K] for -10V
                endpoint_2 = float(scale[1]) # temp in [K] for +10V
                if endpoint_1 > endpoint_2:
                    endpoint_1, endpoint_2 = endpoint_2, endpoint_1
                # Calculate the slope and intercept
                self.slope = (endpoint_2 - endpoint_1) / (volt_high - volt_low)
                self.intercept = self.slope * (-volt_high) + endpoint_2
                self.first_run = False
            # Calculate the corresponding Temperature
            aux_volt =  self.aux_in_3
            value = round(aux_volt*self.slope + self.intercept, 7)
            return value
        return float(value) * magnification

    def autoSensitivity(self):
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
            print('\n', round(percent, 2), 'Sensitivity adjusted\n')
        elif percent > self.SCALE_RANGE_RIGHT:
            self.sensitivity = self.SENSITIVITIES[self.pos + 1]
            self.pos = self.SENSITIVITIES.index(self.sensitivity)
            sleep(self.ADJUST_SCALE_TIME)
            print('\n', round(percent, 2), 'Sensitivity adjusted\n')


if __name__ == '__main__':
    pass
