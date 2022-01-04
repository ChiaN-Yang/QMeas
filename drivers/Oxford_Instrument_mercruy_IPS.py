from lib.driver_interface import DriverInterface
from modpack.mercuryips_GPIB import MercuryIps


class Driver(MercuryIps, DriverInterface):
    METHOD = ['Magnetic field', 'current']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        pass

    def performGetValue(self):
        """Perform the Get Value instrument operation"""
        pass


if __name__ == '__main__':
    pass
