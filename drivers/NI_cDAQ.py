from libs.driver_interface import DriverInterface
import nidaqmx


class Driver(DriverInterface):
    """ This class implements the NI cDAQ driver"""
    METHOD = []

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self, VISA):
        """Perform the operation of opening the instrument connection"""
        with nidaqmx.Task() as self.task:
            self.task.ao_channels.add_ao_voltage_chan(VISA)

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.task.write(0)

    def performSetValue(self, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        self.task.write(value, auto_start=True)
        return value

    def performGetValue(self):
        """Perform the Get Value instrument operation"""
        return self.task.read()


if __name__ == '__main__':
    pass
