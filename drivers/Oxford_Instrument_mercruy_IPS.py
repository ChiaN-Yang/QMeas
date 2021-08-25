from libs.driver_interface import DriverInterface
from libs.mercuryips_GPIB import MercuryIps


class Driver(MercuryIps, DriverInterface):
    METHOD = ['Magnetic field', 'current']

    def __init__(self, VISA, name, type):
        super().__init__(VISA)
        self.Ins_name = name
        self.Ins_type = type
        self.Ins_VISA_add = VISA

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self, options={}):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation"""
        pass

    def performGetValue(self, options={}):
        """Perform the Get Value instrument operation"""
        pass


if __name__ == '__main__':
    pass
