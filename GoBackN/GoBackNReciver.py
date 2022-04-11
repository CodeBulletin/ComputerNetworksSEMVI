import socket
import threading
import time, math
import random

packetDropRate = 0.3

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

def ProcessPacket(packet):
    global Running
    if packet is not None and packet != "":
        if packet == "[e]":
            Running = False

def BinaryToString(binary_message):
    binary_message = int('0b'+binary_message, 2)
    return binary_message.to_bytes((binary_message.bit_length() + 7) // 8, 'big').decode()

mutex = threading.Lock()

Socket = socket.socket()
Reciver_Name = socket.gethostname()
Reciver_IP = socket.gethostbyname(Reciver_Name)

Server_IP = input("Enter Server IP Address: ")
Port = int(input("Enter Port: "))
Name = "GoBackN Reciver"

print(f"My ID: {Reciver_Name}({Reciver_IP})")
print(f"Connecting to: {Server_IP} at port: {Port}")
Socket.connect((Server_IP, Port))

Socket.send(Name.encode())
host_name = Socket.recv(1024).decode()
print(f"Connected to {host_name}")

tot_frames = int(Socket.recv(1024).decode())
print(f"Total Frames: {tot_frames}")

IO = GetInput(Socket)
t = threading.Thread(target=GetInput.Run, args=(IO, ))
t.start()

Running = True
tot_string = ""
Rn = 0

print()
while Running:
    mutex.acquire()
    packet = IO.Get()
    mutex.release()
    ProcessPacket(packet)
    if packet is not None and packet != "" and packet != "[e]":
        packet = packet.split(",")
        print(f"recived packet {packet[0]} | packet data: {packet[1]}", end = " | ")
        if int(packet[0]) == Rn:
            tot_string += packet[1]
            if Rn + 1 < tot_frames:
                print(f"Sending Acknowledgment to get packet {Rn + 1}")
            else:
                print(f"Sending Acknowledgment Transmission Completed")
            if packetDropRate < random.uniform(0, 1):
                time.sleep(0.5)
                Socket.send(f"{Rn}".encode())
            else:
                print(f"Acknowledgment droped!")
            Rn += 1
        else:
            print(f"Sending Acknowledgment to get packet {Rn}")
            if packetDropRate < random.uniform(0, 1):
                time.sleep(0.5)
                Socket.send(f"{Rn - 1}".encode())
            else:
                print(f"Acknowledgment droped!")


print(f"Message Recived: {BinaryToString(tot_string)}")
try:
    Socket.shutdown(socket.SHUT_WR)
except:
    pass
IO.kill()
Socket.close()

t.join()