from packet.util.PacketInterpreter import *


HEADER_SIZE = 6


class Packet:
    def __init__(self, transmission_id, sequence_number):
        self.transmission_id = transmission_id
        self.sequence_number = sequence_number

    def packet(self, data):
        Packet(PacketInterpreter.getTransmissionId(data), PacketInterpreter.getSequenceNumber(data))
    def getSequenceNumber(self):
        return self.sequence_number

    def serialize(self):
        header = struct.pack(self.transmission_id, self.sequence_number)
        return header

    def __str__(self):
        return "Packet{" + \
            "transmissionId= " + str(self.transmission_id) + \
            ", sequenceNumber= " + str(self.sequence_number) + \
            "}"
