# -*- coding: utf-8 -*-
"""
Created on Tue May  4 20:19:18 2021

@author: Tsung-Lin

Progress:
    Successfully query the magnet through the visa address:
        
        TCPIP0::192.168.50.61::7180::SOCKET
    

Issues:
    1. VISA address
    the address is not shown in the visa list. the user has to
    add it or type the address manually.
    
    2. Run error
    The script seems to have a bug when the user run the whole
    script. The solution is to run it separately as two parts:
    1st part: from first line to the mark
    2nd part: after the mark

TODO:
    1. Try to solve the issues
    2. Build up a Class for the Magnet
    3. Test the stability of the script
"""

"""
2021.10.16 

Progress:
    Build the class for the Magnet
    
TODO:
    1. Add more
"""




from lib.driver_interface import DriverInterface
import pyvisa as visa
from time import sleep
import numpy as np
class Driver(DriverInterface):
    METHOD = ['Magnetic Field']

    def __init__(self, visa_address):
        rm = visa.ResourceManager()
        self.magnet = rm.open_resource('TCPIP0::192.168.50.66::7180::SOCKET')
        self.magnet.read_termination = '\r\n'

        # remove hello word
        for i in range(2):
            command = "FIELD:MAGnet?"
            self.magnet.write(command)
            response = self.magnet.read()
        # Pause mode
        command = 'PAUSE'
        self.magnet.write(command)
        sleep(0.1)

    def performOpen(self):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        command = 'PAUSE'
        self.magnet.write(command)
        sleep(0.1)
        self.magnet.close()

    def performSetValue(self, option, value, sweepRate=0.0):
        if option == 'Magnetic Field':
            if value != -999:
                # set target
                command = 'CONFigure:FIELD:TARGet ' + str(value)
                self.magnet.write(command)
                now_value = self.performGetValue(option)
                # ramp mode
                command = 'RAMP'
                self.magnet.write(command)
            else:
                # replace the command by the current field
                # current command is reading the target
                now_value = self.performGetValue(option)
                #print('now_value', now_value, 'self.target', self.target)

        return float(now_value)

    def performGetValue(self, option='0', magnification=1):
        """Perform the Get Value instrument operation"""
        # add the command of current field here
        # e.g.
        if option == 'Magnetic Field':
            command = 'FIELD:MAGnet?'
            self.magnet.write(command)
            value = float(self.magnet.read())
            value *= magnification
            print(value)
        return value

    def experimentLinspacer(self, option, target, speed, increment):
        if int(speed) and increment == '0':
            time_unit = 0.1
            init = float(self.performGetValue(option, 1))
            step = float(speed) / 3600 * time_unit
            if init > float(target):
                step = -step
            result_len = len(np.arange(init, float(target), step))+1
            result = [-999 for _ in range(result_len)]
            result[0] = float(target)
            return result
        elif int(speed) and increment != '0':
            init = float(self.performGetValue(option, 1))
            print('increment', init)
            if init > float(target):
                increment = -float(increment)
            result = np.arange(init, float(target), float(increment))
            result = list(np.append(result, float(target)))
            return result


# =============================================================================
# Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark Mark
# =============================================================================
# command = 'FIELD:TARGet?'
#command = 'FIELD:UNITS?'

# command = 'STATE?'

# heater 1 = open; 0 = close
# command = 'PSwitch 0'

# Ramp / Pause
# command = 'RAMP'
# command = 'PAUSE'

# Field
# command = 'FIELD:TARGet?'
# command = 'CONFigure:FIELD:TARGet 0.0123567'

# #def
# M.write(command)
# response = M.read()

# print('command: ' +  command)
# print('response: ' + response)
