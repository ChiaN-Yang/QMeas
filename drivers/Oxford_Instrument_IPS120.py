from libs.driver_interface import DriverInterface
from libs.ips120 import IPS120
from time import sleep


class Driver(IPS120, DriverInterface):
    METHOD = ['Magnetic field']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        self.setControl(3)
        # Set the LOCAL / REMOTE control state of the IPS 120
        # 0 - Local & Locked (default state)
        # 1 - Remote & Locked
        # 2 - Local & Unlocked
        # 3 - Remote & Locked
        self.setActivity(0)
        # Set the field activation
        # 0 - Hold
        # 1 - To Set Point
        # 2 - To Zero
        # 3 - Clamp (clamp the power supply output)
        self.setHeater(1)
        # Set the switch heater activation state
        # 0 - Heater Off              (close switch)
        # 1 - Heater On if PSU=Magnet (open switch)
        # 2 - Heater On, no checks    (open switch)

    def performClose(self):
        """Perform the close instrument connection operation"""
        # Set the field to zero
        self.setActivity(2)

    def performSetValue(self, value, sweepRate=0.3):
        """Perform the Set Value instrument operation"""
        # Set the magnetic field sweep rate, in Tesla/min
        self.setFieldSweepRate(sweepRate)
        # Set the magnetic field set point, in Tesla
        self.setFieldSetpoint(value)
        # Set the field to Set Point
        self.setActivity(1)
        while abs(value - self.performGetValue()) > 0.1:
            sleep(1)
        now_value = self.performGetValue()
        return now_value

    def performGetValue(self):
        """Perform the Get Value instrument operation"""
        return self.readField()


if __name__ == '__main__':
    pass
