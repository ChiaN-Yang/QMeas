"""Module Oxford Instrument IPS120"""
from qcodes_contrib_drivers.drivers.Oxford.IPS120 import OxfordInstruments_IPS120
from .magnet import Magnet


class OxfordIps120(Magnet):
    """Class Oxford Instrument IPS120"""
    METHOD = ['Magnetic Field', 'Sweeprate Field', 'Switch heater']

    def __init__(self, visa_address):
        super().__init__()
        self.ips120 = OxfordInstruments_IPS120('IPS120',visa_address,True)

    def perform_open(self):
        self.ips120.hold()
        if self.ips120.switch_heater() != self.ips120._GET_STATUS_SWITCH_HEATER[1]:
            self.ips120.switch_heater(1)
            # Set the switch heater activation state
            # 0 - Heater Off              (close switch)
            # 1 - Heater On if PSU=Magnet (open switch)
            # 2 - Heater On, no checks    (open switch)
        init_value = self.perform_get_value('Magnetic Field')
        self.ips120.field_setpoint(init_value)
        self.ips120.sweeprate_field(0.2)
        self.ips120.to_setpoint()
        # Set the field activation
        # 0 - Hold
        # 1 - To Set Point
        # 2 - To Zero
        # 3 - Clamp (clamp the power supply output)

    def perform_close(self):
        self.ips120.hold()
        self.ips120.close()
        # Set the field to zero
        # self.setActivity(2)
        # self.ips120.local()
        # self.ips120.close_all()

    def set_magnetic(self, value):
        self.ips120.field_setpoint(value)

    def get_magnetic(self):
        return self.ips120.field()
