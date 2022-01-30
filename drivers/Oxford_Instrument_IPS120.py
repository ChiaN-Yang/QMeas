from utils import DriverInterface
# from modpack import IPS120
from qcodes_contrib_drivers.drivers.Oxford.IPS120 import OxfordInstruments_IPS120
from time import sleep
import numpy as np


class Driver(OxfordInstruments_IPS120, DriverInterface):
    METHOD = ['Magnetic Field']

    def __init__(self, visa_address):
        self.ips120 = OxfordInstruments_IPS120('IPS120',visa_address,True)
        
        self.ips120.switch_heater(1)
        sleep(0.1)
        # Set the switch heater activation state
        # 0 - Heater Off              (close switch)
        # 1 - Heater On if PSU=Magnet (open switch)
        # 2 - Heater On, no checks    (open switch)
        init_value = self.performGetValue()
        self.ips120.field_setpoint(init_value)
        sleep(0.1)
        self.ips120.activity(1)
        sleep(0.1)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass
        # self.setActivity(0)
        # sleep(0.1)
        # # Set the field activation
        # # 0 - Hold
        # # 1 - To Set Point
        # # 2 - To Zero
        # # 3 - Clamp (clamp the power supply output)

    def performClose(self):
        """Perform the close instrument connection operation"""
        # Set the field to zero
        # self.setActivity(2)
        self.ips120.local()
        sleep(0.1)
        self.ips120.close_all()
        sleep(0.1)

    def performSetValue(self, option, value, sweepRate=0.3):
        """Perform the Set Value instrument operation"""
        if option == 'Magnetic Field':
            if value != np.nan:
                # Set the magnetic field set point, in Tesla
                print('value: ', value)
                self.target = value
                self.ips120.field_setpoint(self.target)
                # Set the field to Set Point
                # print('setActivity')
                # self.setActivity(1)
                # sleep(0.1)
                sleep(0.1)
                now_value = self.performGetValue()
            else:
                now_value = self.ips120.field()
                print('now_value', now_value, 'self.target', self.target)

    def performGetValue(self, option='0', magnification=0):
        """Perform the Get Value instrument operation"""
        return self.ips120.field()

    def experimentLinspacer(self, option, target, speed, increment):
        if int(speed) and increment == '0':
            time_unit = 0.1
            init = self.performGetValue(option, 1)
            step = float(speed) / 3600 * time_unit
            if init > float(target):
                step = -step
            result_len = len(np.arange(init, float(target), step))+1
            result = [np.nan for _ in range(result_len)]
            result[0] = float(target)
            return result
        elif int(speed) and increment != '0':
            init = self.performGetValue(option, 1)
            print('increment', init)
            if init > float(target):
                increment = -float(increment)
            result = np.arange(init, float(target), float(increment))
            result = list(np.append(result, float(target)))
            return result


if __name__ == '__main__':
    mag = Driver("GPIB::25")
