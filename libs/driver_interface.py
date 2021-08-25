import numpy as np


class DriverInterface(object):
    METHOD = []

    def __init__(self, VISA, name, type):
        pass

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, value, options={}, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        pass

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        pass

    def experimentLinspacer(self, target, speed, time_unit, options={}):
        init = self.performGetValue(options)
        step = float(speed) / 3600 * time_unit
        if init > float(target):
            step = -step
        result = np.arange(init, float(target), step)
        result = list(np.append(result, float(target)))
        return result
