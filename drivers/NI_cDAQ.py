from libs.driver_interface import DriverInterface
import nidaqmx


class Driver(DriverInterface):
    """ This class implements the NI cDAQ driver"""
    METHOD = []

    def __init__(self, VISA, name, type):
        self.Ins_name = name
        self.Ins_type = type
        self.Ins_VISA_add = VISA
        self.performOpen(VISA)

    def performOpen(self, VISA, options={}):
        """Perform the operation of opening the instrument connection"""
        with nidaqmx.Task() as self.task:
            self.task.ao_channels.add_ao_voltage_chan(VISA)

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        self.task.write(0)

    def performSetValue(self, value, options={}):
        """Perform the Set Value instrument operation"""
        self.task.write(value, auto_start=True)
        return value

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        return self.task.read()


if __name__ == '__main__':
    pass
