import socket
import threading
import time, math
import random

senderPacketDropRate = 0.1
WaitFor = 4
SendDelay = 0.5

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
        while not self.dead:
            n = time.time()
            if self.running:
                self.t -= n - self.last 
            self.last = n
    
    def TimeOut(self):
        return self.t < 0

    def kill(self):
        self.dead = True
    
class GetInput:
    def __init__(self, Conn):
        self.Conn = Conn
        self.Input: list[str] = []
        self.dead = False

    def Run(self):
        while not self.dead:
            try:
                data = self.Conn.recv(1024).decode()
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
    
    def kill(self):
        self.dead = True

Name = "GoBackN Server"
Socket = socket.socket()
Host = socket.gethostname()
IP = socket.gethostbyname(Host)
Port = 8080

print(f"Host: {Host}({IP}) at Port: {Port}")

Socket.bind((Host, Port))
Socket.listen(1)

Conn, Addr = Socket.accept()
Conn.send(Name.encode())
reciver_name = Conn.recv(1024).decode()
print(f"Connected To: {Addr}, {reciver_name}")

Conn.setblocking(0)

def StringToBinary(message):
    res = ''.join(format(ord(i), '08b') for i in message)
    return res

mutex = threading.Lock()


message = StringToBinary(input("Enter The message: "))
numBitsInFrame = int(input("Number of bytes(char) in one frame: ")) * 8

tot_frames = math.ceil(len(message) / numBitsInFrame)
Conn.send(str(tot_frames).encode())
print(f"Total Frames: {tot_frames}")

Window_size = int(input("Enter the Window Size: "))
Sn = 0
Sb = 0
An = 0

T = Timer(WaitFor)
T.Stop()
T.Reset()
t1 = threading.Thread(target=Timer.Run, args=(T, ))
t1.start()

IO = GetInput(Conn)
t2 = threading.Thread(target=GetInput.Run, args=(IO, ))
t2.start()

print()
while True:
    if Sn < min(Sb + Window_size, tot_frames):
        T.Start()
        data = message[Sn*numBitsInFrame : min((Sn+1)*numBitsInFrame, len(message))]
        print(f"Sending frame {Sn} | data: {data} | Sliding window [{Sb} : {min(Sb + Window_size, tot_frames) - 1}]")
        if senderPacketDropRate <= random.uniform(0, 1):
            time.sleep(SendDelay)
            Conn.send((f"{Sn},"+data).encode())
        else:
            print("Packet Droped!")
        Sn += 1
    mutex.acquire()
    ack = IO.Get()
    mutex.release()
    if ack is not None and ack != "":
        n = int(ack)
        if n == tot_frames - 1:
            print(f"Acknowledgment Recived Transmission Completed")
            break
        else:
            print(f"Acknowledgment Recived to send packet {n + 1}")
        
        Sb = n + 1
        if Sb == Sn:
            T.Stop()
        else:
            T.Reset()
            T.Start()
    if T.TimeOut():
        T.Reset()
        T.Start()
        print("Acknowledgement not recived timed out")
        for i in range(Sb, Sn):
            data = message[i * numBitsInFrame:min((i + 1) * numBitsInFrame, len(message))]
            print(f"Re-sending frame {i} | data: {data} | Sliding window [{Sb} : {min(Sb + Window_size, tot_frames) - 1}]")
            if senderPacketDropRate <= random.uniform(0, 1):
                time.sleep(SendDelay)
                Conn.send((f"{i},"+data).encode())
            else:
                print("Packet Droped!")

Conn.send("[e]".encode())
T.kill()
try:
    Conn.shutdown(socket.SHUT_WR)
except:
    pass
IO.kill()

t1.join()
t2.join()

Conn.close()
Socket.close()