"""Module Bluefors temperature.

Progress:
    Successfully extract the temperature data from the log file.
    The log files are loaded from the NAs address.
"""
import os
from qcodes_contrib_drivers.drivers.BlueFors.BlueFors import BlueFors
from ..instrument import InstrumentDriver


class BlueforsTemperature(InstrumentDriver):
    """Class Bluefors temperature

    Note:
        The logfiles are loaded from NAS address.
    """
    # Please adjust this part if you are using another computer.
    FRIDGE_FOLDER_PATH = "E:\\DATA\\Bluefors_log\\192.168.0.116"
    PROBE_FOLDER_PATH = "E:\\DATA\\Bluefors_log\\192.168.0.115"
    CMETHOD = [
            'CH 1 50K',
            'CH 2 4K',
            'CH 3 Magnet',
            'CH 5 Still',
            'CH 8 MXC',
            'CH 1 Probe'
    ]

    def __init__(self):
        super().__init__()
        if os.path.isdir(self.FRIDGE_FOLDER_PATH) and os.path.isdir(self.PROBE_FOLDER_PATH):
            self.bf_fridge = BlueFors('bf_fridge',
                                      folder_path=self.FRIDGE_FOLDER_PATH,
                                      channel_vacuum_can=1,
                                      channel_pumping_line=2,
                                      channel_compressor_outlet=3,
                                      channel_compressor_inlet=4,
                                      channel_mixture_tank=5,
                                      channel_venting_line=6,
                                      channel_50k_plate=1,
                                      channel_4k_plate=2,
                                      channel_magnet=3,
                                      channel_still=5,
                                      channel_mixing_chamber=8)

            self.bf_probe = BlueFors('bf_probe',
                                     folder_path=self.PROBE_FOLDER_PATH,
                                     channel_vacuum_can=1,
                                     channel_pumping_line=2,
                                     channel_compressor_outlet=3,
                                     channel_compressor_inlet=4,
                                     channel_mixture_tank=5,
                                     channel_venting_line=6,
                                     channel_50k_plate=1,
                                     channel_4k_plate=2,
                                     channel_magnet=3,
                                     channel_still=5,
                                     channel_mixing_chamber=8)
        else:
            self.log.error("Failed to find the file. Please check the file address.")

    def perform_open(self):
        pass

    def perform_close(self):
        self.bf_fridge.close_all()
        self.bf_probe.close_all()

    def perform_set_value(self, option, value, sweep_rate):
        pass

    def perform_get_value(self, option, magnification):
        # TODO: add the command of current field here.
        match option:
            case 'CH 1 Probe':
                value = self.bf_probe.get_temperature(1)
            case 'CH 1 50K':
                value = self.bf_fridge.get_temperature(1)
            case 'CH 2 4K':
                value = self.bf_fridge.get_temperature(2)
            case 'CH 3 Magnet':
                value = self.bf_fridge.get_temperature(3)
            case 'CH 5 Still':
                value = self.bf_fridge.get_temperature(5)
            case 'CH 8 MXC':
                value = self.bf_fridge.get_temperature(8)
            case option:
                self.log.error(f'Option {option} can not be processed')
        return float(value)
