import numpy as np
from ..instrument import InstrumentDriver


class Driver(InstrumentDriver):
    """ This class implements the Time Measurement driver"""
    def __init__(self, time):
        self.time = int(time)
        self.instrument_name = 'Time Meas'

    def __str__(self):
        return self.instrument_name

    def perform_open(self):
        pass

    def perform_close(self):
        pass

    def perform_set_value(self, option, value, sweepRate=0.0):
        return value

    def perform_get_value(self, option, magnification):
        pass

    def experimentLinspacer(self, option, target, speed, increment):
        time = np.arange(0.1, self.time+0.1, 0.1)
        return np.round(time, 2)
