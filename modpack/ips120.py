"""Module containing a class to interface with an Oxford Instruments IPS 120-10.

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    ips120: a class for interfacing with a IPS 120-10 magnet power supply

"""
from datetime import datetime
import time
import logging
import pyvisa as visa

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())

try:
    # the pyvisa manager we'll use to connect to the GPIB resources
    resource_manager = visa.ResourceManager()
except OSError:
    logger.exception(
        "\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")


class IPS120:

    def __init__(self, GPIBaddr):
        """Connect to an IPS 120-10 at the specified GPIB address

        Args:
            GPIBaddr(int): GPIB address of the IPS 120-10
        """
        self._visa_resource = resource_manager.open_resource(GPIBaddr)
        self._visa_resource.read_termination = '\r'
        self.setDisplay('tesla')

    def clear(self):
        self._visa_resource.clear()

    def setControl(self, state=3):
        """Set the LOCAL / REMOTE control state of the IPS 120-10

        0 - Local & Locked (default state)
        1 - Remote & Locked
        2 - Local & Unlocked
        3 - Remote & Locked

        Args:
            state(int): the state in which to place the IPS 120-10
        """
        assert type(state) == int, 'argument must be integer'
        assert state in [0, 1, 2, 3], 'argument must be one of [0,1,2,3]'

        self.clear()
        self._visa_resource.write("$C{}".format(state))

    def readField(self):
        """Read the current magnetic field in Tesla

        Returns:
            field(float): current magnetic field in Tesla
        """
        self.clear()
        self._visa_resource.write('R7')
# =============================================================================
#         self._visa_resource.wait_for_srq()
# =============================================================================
        value_str = self._visa_resource.read()

        return float(value_str.strip('R+'))

    def readcurrent(self):
        """Read the current magnetic field in Tesla

        Returns:
            field(float): current magnetic field in Tesla
        """
        self.clear()
        self._visa_resource.write('R4')
# =============================================================================
#         self._visa_resource.wait_for_srq()
# =============================================================================
        value_str = self._visa_resource.read()

        return float(value_str.strip('R+'))

    def readFieldSetpoint(self):
        """Read the current set point for the magnetic field in Tesla

        Returns:
            setpoint(float): current set point for the magnetic field in Tesla
        """
        self.clear()
        self._visa_resource.write('R8')
# =============================================================================
#         self._visa_resource.wait_for_srq()
# =============================================================================
        value_str = self._visa_resource.read()

        return float(value_str.strip('R+'))

    def readFieldSweepRate(self):
        """Read the current magnetic field sweep rate in Tesla/min

        Returns:
            sweep_rate(float): current magnetic field sweep rate in Tesla/min
        """
        self.clear()
        self._visa_resource.write('R9')
# =============================================================================
#         self._visa_resource.wait_for_srq()
# =============================================================================
        value_str = self._visa_resource.read()
        return float(value_str.strip('R+'))

    def setActivity(self, state=1):
        """Set the field activation method

        0 - Hold  
        1 - To Set Point  
        2 - To Zero  
        3 - Clamp (clamp the power supply output)

        Args:
            state(int): the field activation method
        """
        assert type(state) == int, 'argument must be integer'
        assert state in [0, 1, 2, 3], 'argument must be one of [0,1,2,3]'
        self.clear()
        self._visa_resource.write("A{}".format(state))

    def ReadActivity(self):
        """Set the field activation method

        0 - Hold  
        1 - To Set Point  
        2 - To Zero  
        3 - Clamp (clamp the power supply output)

        Args:
            state(int): the field activation method
        """

        self.clear()
        self._visa_resource.write('X00A0C0H0M00P00')
# =============================================================================
#         self._visa_resource.wait_for_srq()
# =============================================================================

        value_str_1 = str(self._visa_resource.read())
# =============================================================================
#         print(value_str_1)
# =============================================================================
        pos_1 = value_str_1.find('A')

        if value_str_1[pos_1+1] == '0':
            ans_2 = 'Hold'
        elif value_str_1[pos_1+1] == '1':
            ans_2 = 'To Set Point'
        elif value_str_1[pos_1+1] == '2':
            ans_2 = 'To Zero'
        elif value_str_1[pos_1+1] == '3':
            ans_2 = 'Clamp'
        else:
            ans_2 = ''

        Ans = ans_2
        return Ans

    def setHeater(self, state=1):
        """Set the switch heater activation state

        0 - Heater Off              (close switch)
        1 - Heater On if PSU=Magnet (open switch)
        2 - Heater On, no checks    (open switch)

        Args:
            state(int): the switch heater activation state
        """
        assert type(state) == int, 'argument must be integer'
        assert state in [0, 1, 2], 'argument must be one of [0,1,2]'
        self.clear()
        self._visa_resource.write("$H{}".format(state))
        # TODO: add timer to account for time it takes for switch to activate

    def setFieldSetpoint(self, field):
        """Set the magnetic field set point, in Tesla

        Args:
            field(float): the magnetic field set point, in Tesla
        """
        MAX_FIELD = 8
        assert abs(field) < MAX_FIELD, 'field must be less than {}'.format(
            MAX_FIELD)
        self.clear()
        self._visa_resource.write("$J{}".format(field))

    def setFieldSweepRate(self, rate):
        """Set the magnetic field sweep rate, in Tesla/min

        Args:
            rate(float): the magnetic field sweep rate, in Tesla/min
        """
        self.clear()
        self._visa_resource.write("$T{}".format(rate))

    def setDisplay(self, display):
        """Set the display to show amps or tesla

        Args:
            display(str): One of ['amps','tesla']
        """
        assert display in [
            'amps', 'tesla'], "argument must be one of ['amps','tesla']"

        mode_dict = {'amps': 8,
                     'tesla': 9
                     }

        self.clear()
        self._visa_resource.write("$M{}".format(mode_dict[display]))

    def waitForField(self, timeout=600, error_margin=0.01):
        """Wait for the field to reach the set point

        Args:
            timeout(int): maximum time to wait, in seconds
            error_margin(float): how close the field needs to be to the set point, in tesla
        Returns:
            (bool): whether the field set point was reached
        """
        start_time = datetime.now()
        stop_time = start_time + datetime.timedelta(seconds=timeout)

        while datetime.now() < stop_time:
            field = self.readField()
            set_point = self.readFieldSetpoint()

            if abs(field - set_point) < error_margin:
                return True

            time.sleep(5)

        return False

    def shutDown(self):
        self._visa_resource.close()
