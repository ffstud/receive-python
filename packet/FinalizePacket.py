from packet.Packet import *


class FinalizePacket(Packet):
    def __init__(self, data, len):
        super().__init__(PacketInterpreter.getTransmissionId(data), PacketInterpreter.getSequenceNumber(data))
        self.md5 = PacketInterpreter.getByteArrayAt(data, HEADER_SIZE, len - HEADER_SIZE)

    def getMd5(self):
        return self.md5

    def serialize(self):
        header = super().serialize()
        packet_data = struct.pack(f"16s", self.md5)
        return header + packet_data

    def __str__(self):
        return f"FinalizePacket{{" \
               f"md5={self.md5.hex()}, " \
               f"transmissionId={self.transmission_id}, " \
               f"sequenceNumber={self.sequence_number}}}"
