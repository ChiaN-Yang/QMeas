from utils import DriverInterface
# from modpack import IPS120
from qcodes_contrib_drivers.drivers.Oxford.IPS120 import OxfordInstruments_IPS120
from time import sleep
import numpy as np


class Driver(DriverInterface):
    METHOD = ['Magnetic Field']

    def __init__(self, visa_address):
        self.ips120 = OxfordInstruments_IPS120('IPS120',visa_address,True)
        self.first_run = True

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        self.ips120.activity(0)
        if self.first_run:
            self.ips120.switch_heater(1)
            # Set the switch heater activation state
            # 0 - Heater Off              (close switch)
            # 1 - Heater On if PSU=Magnet (open switch)
            # 2 - Heater On, no checks    (open switch)
            self.first_run = False
        init_value = self.performGetValue()
        self.ips120.field_setpoint(init_value)
        self.ips120.sweeprate_field(0.2)
        self.ips120.activity(1)
        # Set the field activation
        # 0 - Hold
        # 1 - To Set Point
        # 2 - To Zero
        # 3 - Clamp (clamp the power supply output)

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.ips120.activity(0)
        # Set the field to zero
        # self.setActivity(2)
        # self.ips120.local()
        # self.ips120.close_all()

    def performSetValue(self, option, value, sweepRate=0.3):
        """Perform the Set Value instrument operation"""
        if option == 'Magnetic Field':
            if value != 'nan':
                # Set the magnetic field set point, in Tesla
                self.target = value
                self.ips120.field_setpoint(self.target)
                now_value = self.performGetValue()
            else:
                now_value = self.performGetValue()
                if now_value == self.target:
                    now_value = 'done'
        return now_value

    def performGetValue(self, option='0', magnification=0):
        """Perform the Get Value instrument operation"""
        return self.ips120.field()

    def experimentLinspacer(self, option, target, speed, increment):
        if increment == '0':
            TIME_UNIT = 0.1
            MAG_SPEED = 12.0
            init = self.performGetValue(option, 1)
            step = MAG_SPEED / 3600 * TIME_UNIT
            if init > float(target):
                step = -step
            result_len = len(np.arange(init, float(target), step))+1
            result = ['nan' for _ in range(result_len)]
            result[0] = float(target)
            return result
        elif increment != '0':
            init = self.performGetValue(option, 1)
            if init > float(target):
                increment = -float(increment)
            result = np.arange(init, float(target), float(increment))
            result = list(np.append(result, float(target)))
            return result


if __name__ == '__main__':
    pass
