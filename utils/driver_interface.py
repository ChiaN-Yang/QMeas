import numpy as np
import abc


class DriverInterface(abc.ABC):
    METHOD = []

    @abc.abstractmethod
    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        return NotImplemented

    @abc.abstractmethod
    def performClose(self):
        """Perform the close instrument connection operation"""
        return NotImplemented

    @abc.abstractmethod
    def performSetValue(self):
        """Perform the Set Value instrument operation"""
        return NotImplemented

    @abc.abstractmethod
    def performGetValue(self):
        """Perform the Get Value instrument operation"""
        return NotImplemented

    def __str__(self):
        return self.instrument_name

    def experimentLinspacer(self, option, target, speed, increment):
        time_unit = 0.1
        init = float(self.performGetValue(option, 1))
        target = float(target)
        speed = int(speed)
        increment = float(increment)
        if speed and increment == 0:
            step = float(speed) / 3600 * time_unit
            if init > target:
                step = -step
            result = np.arange(init, target+step, step)
            return result
        elif speed and increment != 0:
            if init > target and increment > 0:
                increment = -increment
            result = np.arange(init, target+increment, increment)
            return result

    def setProperty(self, visa_address, instrument_name, instrument_type):
        self.instrument_name = instrument_name
        self.instrument_type = instrument_type
        self.instrument_VISA_add = visa_address

    def instrumentName(self):
        return self.instrument_name
