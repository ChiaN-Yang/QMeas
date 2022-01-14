import numpy as np


class TimeMeasurement:
    def __init__(self, time):
        self.time = int(time)
        self.instrument_name = 'Time Meas'

    def performOpen(self, option):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        return value

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        pass

    def experimentLinspacer(self, option, target, speed, increment):
        time = np.arange(0, self.time, 0.1)
        return np.round(time, 2)

    def setProperty(self, visa_address, instrument_name, instrument_type):
        self.instrument_name = instrument_name
        self.instrument_type = instrument_type
        self.instrument_VISA_add = visa_address

    def instrumentName(self):
        return self.instrument_name
