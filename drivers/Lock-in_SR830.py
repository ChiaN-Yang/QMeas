from utils import DriverInterface
from pymeasure.instruments.srs.sr830 import SR830
from time import sleep


class Driver(SR830, DriverInterface):
    METHOD = ['Voltage', 'Frequency', 'Magnitude(R)', 'Magnitude(X)', 'Phase', 'Analog in 1', 'Analog in 2',
              'Magnitude(R) with auto sensitivity', 'Magnitude(X) with auto sensitivity','Triton Temperature (AUX in 3)']

    def __init__(self, visa_address):
        SR830.__init__(self, visa_address)
        self.first_run = True

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

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
                scale = magnification.split(',')
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
            value = aux_volt*self.slope + self.intercept
            return value
        return float(value) * magnification

    def autoSensitivity(self):
        """Set voltage scale to current range"""
        scale_range_L = 0.2
        sacle_range_R = 0.8
        adjust_scale_time = 1.5
        if self.input_config == 'I (1 MOhm)':
            vi_factor = 1e-6
        else:
            vi_factor = 1
        pos_1 = self.SENSITIVITIES.index(self.sensitivity)
        percent_1 = self.magnitude / (self.sensitivity*vi_factor)

        #   Auto range
        # while (percent_1 < Scale_range_L or percent_1 > Sacle_range_R):
        # pos_1 = self.SENSITIVITIES.index(self.sensitivity)
        # percent_1 = self.magnitude / (self.sensitivity*vi_factor)
        if percent_1 < scale_range_L:
            self.sensitivity = self.SENSITIVITIES[pos_1 - 1]
            sleep(adjust_scale_time)
            print('\n', round(percent_1, 2), 'Sensitivity adjusted\n')
        elif percent_1 > sacle_range_R:
            self.sensitivity = self.SENSITIVITIES[pos_1 + 1]
            sleep(adjust_scale_time)
            print('\n', round(percent_1, 2), 'Sensitivity adjusted\n')


if __name__ == '__main__':
    pass
