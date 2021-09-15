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

    def experimentLinspacer(self, option, target):
        init = self.performGetValue(option)
        print('init', init)
        step = float(self.speed) / 3600 * self.time_unit
        if init > float(target):
            step = -step
        result = np.arange(init, float(target), step)
        result = list(np.append(result, float(target)))
        return result

    def setControlOption(self, speed, time_unit):
        self.speed = speed
        self.time_unit = time_unit

    def setReadOption(self, magnification):
        self.magnification = magnification

    def setProperty(self, visa_address, instrument_name, instrument_type):
        self.instrument_name = instrument_name
        self.instrument_type = instrument_type
        self.instrument_VISA_add = visa_address

    def instrumentName(self):
        return self.instrument_name
