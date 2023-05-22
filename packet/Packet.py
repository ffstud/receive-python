from packet.util.PacketInterpreter import *


class Packet:
    HEADER_SIZE = 6

    def __init__(self, transmission_id, sequence_number):
        self.transmission_id = transmission_id
        self.sequence_number = sequence_number

    def packet(self, data):
        Packet(PacketInterpreter.getTransmissionId(data), PacketInterpreter.getSequenceNumber(data))

    def getSequenceNumber(self):
        return self.sequence_number

    def serialize(self):
        byte_buffer = bytearray(self.HEADER_SIZE)
        byte_buffer[0:2] = self.transmission_id.to_bytes(2, byteorder='big')
        byte_buffer[2:6] = self.sequence_number.to_bytes(4, byteorder='big')
        return byte_buffer

    def __str__(self):
        return "Packet{" + \
            "transmissionId= " + str(self.transmission_id) + \
            ", sequenceNumber= " + str(self.sequence_number) + \
            "}"
