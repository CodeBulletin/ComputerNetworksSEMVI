import json
import CRC_Python
import enum

class AckFrame:
    def __init__(self, atype, ack_no):
        self.atype = atype
        self.ack_no = ack_no
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Frame:
    def __init__(self, frameNo, data=""):
        self.frameNo = frameNo
        self.data = data

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def EncodeFrame(frame) -> str:
    return frame.toJSON().encode()

def DecodeFrame(Dict) -> Frame:
    return Frame(**Dict)

def DecodeAckFrame(Dict) -> AckFrame:
    return AckFrame(**Dict)