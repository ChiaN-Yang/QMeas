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
        if int(speed) and increment == '0':
            init = self.performGetValue(option, 1)
            print('speed', init)
            step = float(speed) / 3600 * time_unit
            if init > float(target):
                step = -step
            result = np.arange(init, float(target), step)
            result = list(np.append(result, float(target)))
            return result
        elif int(speed) and increment != '0':
            init = self.performGetValue(option, 1)
            print('increment', init)
            if init > float(target):
                increment = -float(increment)
            result = np.arange(init, float(target), float(increment))
            result = list(np.append(result, float(target)))
            return result

    def setProperty(self, visa_address, instrument_name, instrument_type):
        self.instrument_name = instrument_name
        self.instrument_type = instrument_type
        self.instrument_VISA_add = visa_address

    def instrumentName(self):
        return self.instrument_name
