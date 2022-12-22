"""Module Oxford Instrument mercruy IPS"""
from .magnet import Magnet


class Driver(Magnet):
    """Class Oxford Instrument mercruy IPS"""
    METHOD = ['Magnetic field', 'current']

    def __init__(self, visa_address):
        super().__init__(visa_address)

    def perform_open(self):
        pass

    def perform_close(self):
        pass

    def set_magnetic(self, value):
        pass

    def get_magnetic(self):
        pass
