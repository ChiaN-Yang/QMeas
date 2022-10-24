"""Driver NI cDAQ"""
import nidaqmx
from ..instrument import InstrumentDriver


class NiCdaq(InstrumentDriver):
    """ This class implements the NI cDAQ driver"""
    METHOD = ['ao0', 'ao1', 'ao2', 'ao3']

    def __init__(self):
        super().__init__()
        self.__set_voltage_zero()

    def __set_voltage_zero(self):
        with nidaqmx.Task() as task:
            for channel in self.METHOD:
                task.ao_channels.add_ao_voltage_chan(f'{self.address}/{channel}')
            task.write([[0], [0], [0], [0]], auto_start=True)
        self.value = {
                self.METHOD[0]: 0,
                self.METHOD[2]: 0,
                self.METHOD[2]: 0,
                self.METHOD[3]: 0
        }

    def perform_open(self):
        pass

    def perform_close(self):
        pass

    def perform_set_value(self, option, value, sweep_rate=0.0):
        if option in self.METHOD:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f'{self.address}/{option}')
                task.write(value, auto_start=True)
            self.value[option] = value
        else:
            self.log.error(f'Option {option} can not be processed')
        return value

    def perform_get_value(self, option, magnification):
        return self.value[option]
