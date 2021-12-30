# -*- coding: utf-8 -*-
"""
Created on Tue May  4 20:19:18 2021

@author: Tsung-Lin

Progress:
    1. Successfully extract the temperature data from the log file.
    2. The log files are loaded from the NAs address.
"""

from libs.driver_interface import DriverInterface
from qcodes_contrib_drivers.drivers.BlueFors.BlueFors import BlueFors
import os
class Driver(DriverInterface):
    METHOD = ['CH 1 50K',
              'CH 2  4K',
              'CH 3 Magnet',
              'CH 4 Still',
              'CH 8 MXC',
              'CH 1 Probe']

    def __init__(self, visa_address):
        # The logfiles are loaded from NAS address. Please adjust this part if 
        # you are using another computer.
        fridge_folder_path = "Z:\\BlueforsLog\\log-data\\192.168.0.116"
        probe_folder_path = "Z:\\BlueforsLog\\log-data\\192.168.0.115"
        if not os.path.isdir(fridge_folder_path) and os.path.isdir(probe_folder_path): 
          print("Failed to find the file. Please check the file address.")
        else:
            self.bf_fridge = BlueFors('bf_fridge',
                          folder_path=fridge_folder_path,
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
                          folder_path=probe_folder_path,
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

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        self.bf_fridge.close_all()
        self.bf_probe.close_all()

    def performSetValue(self, option, value, sweepRate=0.0):
        pass

    def performGetValue(self, option='0', magnification=1):
        """Perform the Get Value instrument operation"""
        # add the command of current field here
        # e.g.
        if option =='CH 1 Probe':
            probe_channel_num = 1
            value = self.bf_probe.get_temperature(probe_channel_num) 
        elif option == 'CH 1 50K':
            channel_num = 1
            value = self.bf_fridge.get_temperature(channel_num) 
        elif option == 'CH 2  4K':
            channel_num = 2
            value = self.bf_fridge.get_temperature(channel_num) 
        elif option == 'CH 3 Magnet':
            channel_num = 3 
            value = self.bf_fridge.get_temperature(channel_num)                
        elif option == 'CH 4 Still':
            channel_num = 4   
            value = self.bf_fridge.get_temperature(channel_num)              
        elif option == 'CH 8 MXC':
            channel_num = 8                
            value = self.bf_fridge.get_temperature(channel_num) 
        return float(value)
