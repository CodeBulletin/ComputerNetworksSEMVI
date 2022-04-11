import time

class Timer:
    def __init__(self, value):
        self.value = value
        self.t = value
        self.running = True
        self.dead = False

    def Start(self):
        self.running = True
    
    def Reset(self):
        self.t = self.value
    
    def Stop(self):
        self.running = False
    
    def Run(self):
        self.last = time.time()
        while not self.dead:
            n = time.time()
            if self.running:
                self.t -= n - self.last 
            self.last = n
    
    def TimeOut(self):
        return self.t < 0

    def kill(self):
        self.dead = True


