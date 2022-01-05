from lib.driver_interface import DriverInterface
import nidaqmx


class Driver(DriverInterface):
    """ This class implements the NI cDAQ driver"""
    METHOD = ['ao0', 'ao1', 'ao2', 'ao3']

    def __init__(self, visa_address):
        self.address = visa_address
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao0")
            task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao1")
            task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao2")
            task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao3")
            task.write([[0], [0], [0], [0]], auto_start=True)
        self.value = 0

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        if option == 'ao0':
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao0")
                task.write(value, auto_start=True)
        elif option == 'ao1':
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao1")
                task.write(value, auto_start=True)
        elif option == 'ao2':
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao2")
                task.write(value, auto_start=True)
        elif option == 'ao3':
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f"{self.address}/ao3")
                task.write(value, auto_start=True)
        self.value = value
        return value

    def performGetValue(self, option, magnification):
        """Perform the Get Value instrument operation"""
        return self.value


if __name__ == '__main__':
    pass
