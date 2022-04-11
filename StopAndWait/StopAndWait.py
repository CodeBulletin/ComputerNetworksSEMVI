import time
import random
import string
import threading
import CRC_Python

#Helper functions and variables
def GenerateRandomString(length):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))
    return res

def StringToBinary(message):
    res = ''.join(format(ord(i), '08b') for i in message)
    return res

def BinaryToString(binary_message):
    binary_message = int('0b'+binary_message, 2)
    return binary_message.to_bytes((binary_message.bit_length() + 7) // 8, 'big').decode()

def Flip(a):
    if a == '1':
        return '0'
    return '1'

def FlipBits(binary_message, errorRate):
    for i in range(len(binary_message)):
        if random.uniform(0, 1) < errorRate:
            binary_message = binary_message[:i] + Flip(binary_message[i]) + binary_message[i+1:]
    return(binary_message)

Poly = "11000000000000101"
mutex = threading.Lock()


# main code

class Packet:
    def __init__(self, data: int):
        self.data = data

class frame:
    def __init__(self, frameNo: int, packet: Packet):
        self.frameNo = frameNo
        self.packet = packet

class ack_frame:
    def __init__(self, ack_type: int):
        self.ack_type = ack_type

#Variables
message_len = 64
packets = 5
seq = 4
waitFor = 4

networkDelayRange = [0, 0]
errorRate = 0.00001
acknowledgementDropRate = 0.01
frameDropRate = 0.01

completed = False
sf = None
rf = None

#networking functions
def FromNetworkLayer(message):
    return Packet(CRC_Python.EncodeCRC(StringToBinary(message), Poly))

def ToNetworkLayer(Frame):
    mutex.acquire()
    frame = ack_frame(0)
    if not CRC_Python.ValidateCRC(Frame.packet.data, Poly):
        frame.ack_type = 1
        print("\nReceiver:")
        print(f"Received Frame: {Frame.frameNo + 1}")
        print("Received data has errors")
    else:
        print("\nReceiver:")
        print(f"Received Frame: {Frame.frameNo + 1}")
        print(f"Packet Data: {BinaryToString(CRC_Python.RemoveZeros(Frame.packet.data, len(Poly) - 1))}")
    mutex.release()
    return frame

def ToPhysicalLayer(Frame, isSender):
    mutex.acquire()
    delay = random.uniform(networkDelayRange[0], networkDelayRange[1])
    time.sleep(delay)
    if isSender:
        if frameDropRate < random.uniform(0, 1):
            Frame.packet.data = FlipBits(Frame.packet.data, errorRate)
            global sf
            sf = Frame
    else:
        if acknowledgementDropRate < random.uniform(0, 1):
            global rf
            rf = Frame
    mutex.release()

def FromPhysicalLayer(isSender):
    if(isSender):
        mutex.acquire()
        global rf
        Frame = ack_frame(rf.ack_type)
        rf = None
        mutex.release()
        return Frame
    else:
        mutex.acquire()
        global sf
        Frame = frame(sf.frameNo, Packet(sf.packet.data))
        sf = None
        mutex.release()
        return Frame

def WaitForReceiver():
    t_end = time.time() + waitFor
    while time.time() < t_end and rf == None:
        pass
    if time.time() < t_end:
        return True
    return False

def WaitForSender():
    while sf == None and not completed:
        pass

def isCompleted():
    return completed


# Sender
def Sender(num_packets):
    messages = [GenerateRandomString(message_len) for i in range(num_packets)]
    i = 0
    error = 0
    eM = "None"
    while i < num_packets:
        m = messages[i]
        packet = FromNetworkLayer(m)
        Frame = frame(i, packet)

        mutex.acquire()
        print("\nSender:")
        if error != 0:
            print(f"Resending packet {i+1} for Reason: {eM}")
        else:
            print(f"Sending Frame: {i+1}")
        print(f'Packet data: {m}')
        mutex.release()

        ToPhysicalLayer(Frame, True)

        got_ack = WaitForReceiver()
        if got_ack:
            error = 0
            rFrame = FromPhysicalLayer(True) 
            mutex.acquire()
            print("\nSender:")
            print(f"Acknowledgement received for packet {i+1}")
            mutex.release()
            if rFrame.ack_type == 1:
                error = 1
                eM = "Message got corrupted during transmission"
                i -= 1
        else:
            i -= 1
            eM = "acknowledgement not recevied"
            error = 1
        i += 1
    mutex.acquire()
    global completed
    completed = True
    mutex.release()


# Receiver
def Receiver(num_packets):
    while not isCompleted():
        WaitForSender()
        if not isCompleted():
            Frame = FromPhysicalLayer(False)
            aFrame = ToNetworkLayer(Frame)
            ToPhysicalLayer(aFrame, False)


for i in range(seq):
    print(f"\nSequence: {i}")
    t1 = threading.Thread(target=Sender, args=(packets, ))
    t2 = threading.Thread(target=Receiver, args=(packets, ))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    completed = False
