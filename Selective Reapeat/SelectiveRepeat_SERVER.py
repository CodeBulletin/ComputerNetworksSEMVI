import socket, time, math, threading, json, random
import NetworkIO
import Timer as T
import Frames
import CRC_Python

WaitFor = 4
numMessageBits = 8
FrameDelay = [0.25, 0.75]
FrameDropRate = 0.1
bitErrorRate = 0.01
poly = "11110111"

def StringToBinary(message):
    res = ''.join(format(ord(i), '08b') for i in message)
    return res

def GenerateBitError(message):
    new_message = message
    for i in range(len(message)):
        if random.uniform(0, 1) <= bitErrorRate:
            bit = str(abs(int(new_message[i]) - 1))
            new_message = new_message[0:i] + bit + new_message[i+1:]
    return new_message

def FromNetworkLayer(bin_m, i, num_bits):
    m = bin_m[i*num_bits : min((i+1)*num_bits, len(bin_m))]
    return CRC_Python.EncodeCRC(m, poly)

def StartTimer(SN, Dict):
    tr = T.Timer(WaitFor)
    th = threading.Thread(target=T.Timer.Run, args=(tr, ))
    th.start()
    Dict[SN] = [tr, th]

def StopTimer(SN, Dict):
    if SN in Dict:
        tr, th = Dict[SN]
        tr.kill()
        th.join()
        Dict.pop(SN)

def RestartTimer(SN, Dict):
    if SN in Dict:
        tr = Dict[SN][0]
        tr.Reset()

def AnyTimeOut(Dict):
    for i in Dict:
        tr = Dict[i][0]
        if tr.TimeOut():
            return i
    return None

def droped():
    return FrameDropRate > random.uniform(0, 1)

mutex = threading.Lock()
Port = 8080
ServerName = "SR_SERVER"
Socket = socket.socket()

HostName = socket.gethostname()
IP = socket.gethostbyname(HostName)
Socket.bind((HostName, Port))

print(f"Server Started {HostName}({IP}) at {Port}")

Socket.listen(1)
Conn, Address = Socket.accept()
Conn.send(ServerName.encode())
ClientName = Conn.recv(1024).decode()

print(f"Connected to client {ClientName}, Address: {Address}")

message = input("Enter the message to send: ")

SW = int(input("Enter Sliding Window Size: "))

Binary = StringToBinary(message)
Tot_Frames = math.ceil(len(Binary) / numMessageBits)
Conn.send(f"{Tot_Frames}".encode())

timers = {}

IO = NetworkIO.IO(Conn, 4096, mutex)
transmitted = [False for i in range(Tot_Frames)]

t1 = threading.Thread(target=NetworkIO.IO.Run, args=(IO, ))
t1.start()
SB = 0
SN = 0

while True:
    if SN - SB < SW and SN < Tot_Frames:
        print(f"Sending Frame {SN} | Window: [{SB} - {min(Tot_Frames, SB + SW) - 1}]")
        StartTimer(SN, timers)
        if not droped():
            data = GenerateBitError(FromNetworkLayer(Binary, SN, numMessageBits))
            f = Frames.Frame(SN, data)
            delay = random.uniform(FrameDelay[0], FrameDelay[1])
            IO.Send(delay, Frames.EncodeFrame(f))
        else:
            print("Frame Droped")
        SN = SN + 1
    
    mutex.acquire()
    frame = IO.Get()
    mutex.release()
    if frame is not None and frame != "":
        af = Frames.DecodeAckFrame(json.loads(frame))
        if af.atype == 0:
            print(f"Acknowledgement recived for Frame {af.ack_no} | Window: [{SB} - {min(Tot_Frames, SB + SW) - 1}]")
            if (af.ack_no >= SB and af.ack_no <= min(Tot_Frames, SB + SW) - 1):
                StopTimer(af.ack_no, timers)
                transmitted[af.ack_no] = True
                if af.ack_no == SB:
                    while SB < Tot_Frames and transmitted[SB] != False:
                        SB += 1

                if SB == Tot_Frames:
                    break
        elif af.atype == 1:
            if af.ack_no >= SB and af.ack_no <= min(Tot_Frames, SB + SW) - 1:
                print(f"Negative Acknowledgement recived for Frame {af.ack_no}  | Window: [{SB} - {min(Tot_Frames, SB + SW) - 1}]")
                print(f"Resending Frame {af.ack_no}")
                RestartTimer(af.ack_no, timers)
                if not droped():
                    data = GenerateBitError(FromNetworkLayer(Binary, af.ack_no, numMessageBits))
                    f = Frames.Frame(af.ack_no, data)
                    delay = random.uniform(FrameDelay[0], FrameDelay[1])
                    IO.Send(delay, Frames.EncodeFrame(f))
                else:
                    print("Frame Droped")
    
    TN = AnyTimeOut(timers)
    if TN is not None:
        print(f"Timed Out, Acknowledgement not recived for frame {TN} in time | Window: [{SB} - {min(Tot_Frames, SB + SW) - 1}]")
        print(f"Resending Frame {TN}")
        RestartTimer(TN, timers)
        if not droped():
            data = GenerateBitError(FromNetworkLayer(Binary, TN, numMessageBits))
            f = Frames.Frame(TN, data)
            delay = random.uniform(FrameDelay[0], FrameDelay[1])
            IO.Send(delay, Frames.EncodeFrame(f))
        else:
            print("Frame Droped")
Conn.send("[e]".encode())

Conn.shutdown(socket.SHUT_RDWR)
IO.kill()
Conn.close()
Socket.close()

t1.join()