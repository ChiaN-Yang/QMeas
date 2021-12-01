from libs.driver_interface import DriverInterface
from libs.ips120 import IPS120
from time import sleep
import numpy as np


class Driver(IPS120, DriverInterface):
    METHOD = ['Magnetic Field']

    def __init__(self, visa_address):
        super().__init__(visa_address)
        
        self.setControl(3)
        sleep(0.1)
        # Set the LOCAL / REMOTE control state of the IPS 120
        # 0 - Local & Locked (default state)
        # 1 - Remote & Locked
        # 2 - Local & Unlocked
        # 3 - Remote & Unlocked
        self.setHeater(1)
        sleep(0.1)
        # Set the switch heater activation state
        # 0 - Heater Off              (close switch)
        # 1 - Heater On if PSU=Magnet (open switch)
        # 2 - Heater On, no checks    (open switch)
        init_value = self.performGetValue()
        self.setFieldSetpoint(init_value)
        sleep(0.1)
        self.setActivity(1)
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
        self.setControl(2)
        sleep(0.1)
        self.shutDown()

    def performSetValue(self, option, value, sweepRate=0.3):
        """Perform the Set Value instrument operation"""
        if option == 'Magnetic Field':
            if value != -999:
                # Set the magnetic field set point, in Tesla
                print('value: ',value)
                self.target = value
                self.setFieldSetpoint(self.target)
                # Set the field to Set Point
                # print('setActivity')
                # self.setActivity(1)
                # sleep(0.1)
                sleep(0.1)
                now_value = self.performGetValue()
            else:
                now_value = self.readField()
                print('now_value', now_value, 'self.target', self.target)

    def performGetValue(self, option='0', magnification=0):
        """Perform the Get Value instrument operation"""
        return self.readField()
    
    def experimentLinspacer(self, option, target, speed, increment):
        if int(speed) and increment == '0':
            time_unit = 0.1
            init = self.performGetValue(option, 1)
            step = float(speed) / 3600 * time_unit
            if init > float(target):
                step = -step
            result_len = len(np.arange(init, float(target), step))+1
            result = [-999 for _ in range(result_len)]
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
    pass
