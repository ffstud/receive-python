from src.packet.Packet import *


class DataPacket(Packet):
    def __init__(self, data):
        super().__init__(data, PacketInterpreter.getSequenceNumber(data))
        self.transmission_id = PacketInterpreter.getTransmissionId(data)
        self.data = data[HEADER_SIZE:]

    def getData(self):
        return self.data

    def serialize(self):
        header = super().serialize()
        byte_buffer = bytearray(HEADER_SIZE + len(self.data))
        byte_buffer[0:HEADER_SIZE] = header
        byte_buffer[HEADER_SIZE:] = self.data
        return byte_buffer

    def __str__(self):
        return f"DataPacket{{data={self.data}, " \
               f"transmission_id={self.transmission_id}, " \
               f"sequence_number={self.sequence_number}}}"

