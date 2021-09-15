from libs.driver_interface import DriverInterface
import nidaqmx


class Driver(DriverInterface):
    """ This class implements the NI cDAQ driver"""
    METHOD = ['ao0', 'a01', 'ao2', 'ao3']

    def __init__(self, visa_address):
        self.chanel_count = 0

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        self.task = nidaqmx.Task()

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'ao0':
            self.task.ao_channels.add_ao_voltage_chan("cDAQ1Mod1/ao0")
            self.task.write(value, auto_start=True)
        elif option == 'ao1':
            self.task.ao_channels.add_ao_voltage_chan("cDAQ1Mod1/ao1")
            self.task.write(value, auto_start=True)
        elif option == 'ao2':
            self.task.ao_channels.add_ao_voltage_chan("cDAQ1Mod1/ao2")
            self.task.write(value, auto_start=True)
        elif option == 'ao3':
            self.task.ao_channels.add_ao_voltage_chan("cDAQ1Mod1/ao3")
            self.task.write(value, auto_start=True)
        return value

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        return self.task.read()


if __name__ == '__main__':
    pass
