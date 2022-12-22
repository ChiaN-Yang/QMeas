"""Module magnet"""
import abc
import numpy as np
from ..instrument import InstrumentDriver


class Magnet(InstrumentDriver):
    """Class magnet"""
    METHOD = ['Magnetic Field']
    MAG_SPEED = 12.0

    def __init__(self):
        super().__init__()
        self.target = 0

    def perform_set_value(self, option, value, sweep_rate):
        match option:
            case 'Magnetic Field':
                if value != 'nan':
                    self.target = value
                    now_value = self.perform_get_value('Magnetic Field')
                    self.set_magnetic(self.target)
                else:
                    now_value = self.perform_get_value('Magnetic Field')
                    if now_value == self.target:
                        now_value = 'done'
            case 'Sweeprate Field':
                self.set_sweeprate_field(value)
                now_value = 'done'
            case 'Switch heater':
                self.set_switch_heater(value)
                now_value = 'done'
        return now_value

    @abc.abstractmethod
    def set_magnetic(self, value: float) -> float:
        """Set magnetic field

        Args:
            value (float): The set value.
        """
        return NotImplemented

    @abc.abstractmethod
    def set_sweeprate_field(self, value: float) -> float:
        """Set sweeprate field

        Args:
            value (float): The set value.
        """
        return NotImplemented

    @abc.abstractmethod
    def set_switch_heater(self, value: int) -> int:
        """Set switch heater

        Args:
            value (int): One for open and zero for close.
        """
        return NotImplemented

    def perform_get_value(self, option, magnification=1):
        if option == 'Magnetic Field':
            value = self.get_magnetic()*magnification
        else:
            self.log.error(f'Option {option} can not be processed')
        return value

    @abc.abstractmethod
    def get_magnetic(self) -> float:
        """Set switch heater

        Args:
            value (int): One for open and zero for close.
        """
        return NotImplemented

    def setpoints(self, option, target, speed, increment):
        match option:
            case 'Sweeprate Field':
                return [target]
            case 'Switch heater':
                return [target]
            case 'Magnetic Field':
                init = self.perform_get_value('Magnetic Field', 1)
                if increment == 0:
                    step_num = int(abs(target-init)/self.MAG_SPEED*3600/self.TIME_UNIT)
                    result_len = len(np.linspace(init, target, step_num))
                    if result_len:
                        result = ['nan' for _ in range(result_len)]
                        result[0] = target
                    else:
                        result = [target]
                else:
                    if init > target and increment > 0:
                        increment = -increment
                    result = np.arange(init, target+increment, increment)
                return result
