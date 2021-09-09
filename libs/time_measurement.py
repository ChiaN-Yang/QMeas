class TimeMeasurement:
    def __init__(self, time):
        self.time = int(time)
        self.instrument_name = 'Time Meas'

    def performOpen(self, option):
        """Perform the operation of opening the instrument connection"""
        pass

    def performClose(self):
        """Perform the close instrument connection operation"""
        pass

    def performSetValue(self, option, value, sweepRate=0.0):
        """Perform the Set Value instrument operation"""
        return value

    def performGetValue(self, option):
        """Perform the Get Value instrument operation"""
        pass

    def experimentLinspacer(self, option, target):
        return range(self.time*10)
    
    def setControlOption(self, speed, time_unit):
        self.speed = speed
        self.time_unit = time_unit

    def setReadOption(self, magnification):
        self.magnification = magnification

    def getLevel(self):
        return self.level

    def setProperty(self, visa_address, instrument_name, instrument_type):
        self.instrument_name = instrument_name
        self.instrument_type = instrument_type
        self.instrument_VISA_add = visa_address
        
    def instrumentName(self):
        return self.instrument_name
