"""Module instrument driver interface"""
import abc
import logging
import numpy as np


class InstrumentDriver(abc.ABC):
    """Class instrument driver interface"""
    METHOD = []
    TIME_UNIT = 0.1

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger('Instrument')
        self.name = None
        self.type = None
        self.address = None

    def __str__(self):
        return self.name

    @abc.abstractmethod
    def perform_open(self) -> None:
        """Perform the operation of opening the instrument connection"""
        return NotImplemented

    @abc.abstractmethod
    def perform_close(self) -> None:
        """Perform the close instrument connection operation"""
        return NotImplemented

    @abc.abstractmethod
    def perform_set_value(self, option: str, value: float, sweep_rate: float) -> float:
        """Perform the Set Value instrument operation

        Args:
            option (str): The instrument option.
            value (float): The set vlaue.
            sweep_rate (float): The sweep rate.

        Returns:
            float: The set value.
        """
        return NotImplemented

    @abc.abstractmethod
    def perform_get_value(self, option: str, magnification: float) -> float:
        """Perform the Get Value instrument operation

        Args:
            option (str): The instrument option.
            magnification (float): The sweep rate.

        Returns:
            float: The get value.
        """
        return NotImplemented

    def setpoints(self, option: str, target: float, speed: float, increment: float) -> list:
        """Create arithmetic progression for set value function.

        Args:
            option (str): The instrument option.
            target (float): The set point target.
            speed (float): The set point speed.
            increment (float): The set point increment.

        Returns:
            list: The set points list.
        """
        init = self.perform_get_value(option, 1)
        if speed and not increment:
            step_num = int(abs(target-init)/speed*3600/self.TIME_UNIT)
            result = np.linspace(init, target, step_num)
        elif speed and increment:
            if init > target and increment > 0:
                increment = -increment
            result = np.arange(init, target+increment, increment)
        else:
            self.log.error('The setpoint function missing parameter.')
        return result

    def set_property(self, visa_address, instrument_name, instrument_type):
        """Set instrument property."""
        self.name = instrument_name
        self.type = instrument_type
        self.address = visa_address
