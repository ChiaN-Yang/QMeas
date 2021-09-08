class TimeMeasurement:
    def __init__(self, time):
        self.time = time

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

    def experimentLinspacer(self, option):
        return range(self.time*10)
