import socket
import time
import threading

class IO:
    def __init__(self, Conn, Size, mutex):
        self.Conn = Conn
        self.Input: list[str] = []
        self.Size = Size
        self.dead = False
        self.mutex = mutex

    def Run(self):
        while not self.dead:
            try:
                data = self.Conn.recv(self.Size).decode()
                self.Input.append(data)
            except:
                pass
    
    def Get(self):
        if len(self.Input) == 0:
            return None
        else:
            data = self.Input[0]
            self.Input = self.Input[1:]
            return data

    def __Send(self, data):
        self.mutex.acquire()
        self.Conn.send(data)
        self.mutex.release()

    def Send(self, wait, data):
        th = threading.Timer(wait, IO.__Send, [self, data])
        th.start()
        
    def kill(self):
        self.dead = True