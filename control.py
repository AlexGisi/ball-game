class pid:
    def __init__(self, kp, kd, ki):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        
        self.e_last = 0
        self.e_cum = 0
        
    def control(self, error):
        de = error - self.e_last
        self.e_last = error
        self.e_cum += error
        
        return error * self.kp + de * self.kd + self.ki * self.e_cum
        