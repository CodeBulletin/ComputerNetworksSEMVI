import socket, time, math, threading, json, random
import NetworkIO
import Frames
import CRC_Python

ack_delay = [0.25, 0.75]
ack_drop_rate = 0.1
poly = "11110111"

def BinaryToString(binary_message):
    binary_message = int('0b'+binary_message, 2)
    return binary_message.to_bytes((binary_message.bit_length() + 7) // 8, 'big').decode()

def droped():
    return ack_drop_rate > random.uniform(0, 1)

mutex = threading.Lock()
Socket = socket.socket()
ClientName = "SR_CLIENT"

IP = input("Enter the server IP address: ")
Port = int(input("Enter The Port: "))

Socket.connect((IP, Port))
SERVER_NAME = Socket.recv(1024).decode()
Socket.send(ClientName.encode())
print(f"Connected to server: {SERVER_NAME}")

Tot_Frames = int(Socket.recv(1024).decode())
print(f"Total number of frames {Tot_Frames}")

message = [False for i in range(Tot_Frames)]
IO = NetworkIO.IO(Socket, 4096, mutex)

t1 = threading.Thread(target=NetworkIO.IO.Run, args=(IO, ))
t1.start()

RN = 0
while True:
    mutex.acquire()
    frame = IO.Get()
    mutex.release()
    if frame is not None and frame != "":
        if frame != "[e]":
            f = Frames.DecodeFrame(json.loads(frame))
            print(f"Recived frame {f.frameNo} | Data {f.data}")
            if CRC_Python.ValidateCRC(f.data, poly):
                if message[f.frameNo] == False:
                    message[f.frameNo] = CRC_Python.RemoveZeros(f.data, len(poly) - 1)
                
                print(f"sending ACK for frame {f.frameNo}")

                af = Frames.AckFrame(0, f.frameNo)
                if not droped():
                    delay = random.uniform(ack_delay[0], ack_delay[1])
                    IO.Send(delay, Frames.EncodeFrame(af))
                else:
                    print("ACK Droped")
                if RN == f.frameNo:
                    while RN < Tot_Frames and message[RN] != False:
                        RN += 1
            else:
                # Message is corrupted
                print(f"Error in Recived Frame sending NACK for frame {f.frameNo}")

                af = Frames.AckFrame(1, f.frameNo)
                if not droped():
                    delay = random.uniform(ack_delay[0], ack_delay[1])
                    IO.Send(delay, Frames.EncodeFrame(af))
                else:
                    print("NACK Droped")
        else:
            break
Message = BinaryToString("".join(message))
print(f"Recived Message: {Message}")

Socket.shutdown(socket.SHUT_RDWR)
IO.kill()
Socket.close()
t1.join()