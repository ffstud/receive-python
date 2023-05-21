from packet.Packet import *


# noinspection PyRedeclaration
class InitializePacket(Packet):
    HEADER_SIZE = 6
    def __init__(self, data, length):
        super().__init__(PacketInterpreter.getTransmissionId(data), PacketInterpreter.getSequenceNumber(data))
        self.max_sequence_number = PacketInterpreter.getUIntAt(data, self.HEADER_SIZE)
        self.file_name = PacketInterpreter.getStringAt(data, self.HEADER_SIZE + 4, length - (self.HEADER_SIZE + 4))

    def getSequenceNumber(self):
        return self.sequence_number

    def getMaxSequenceNumber(self):
        return self.max_sequence_number

    def setMaxSequenceNumber(self, maxSequenceNumber):
        self.maxSequenceNumber = maxSequenceNumber

    def getFileName(self):
        return self.fileName

    def setFileName(self, fileName):
        self.fileName = fileName

    def serialize(self):
        header = super().serialize()
        fileNameBytes = codecs.encode(self.fileName, 'utf-8')
        payloadLength = len(fileNameBytes) + 4
        payloadFormat = f">I{payloadLength}s"
        payload = struct.pack(payloadFormat, self.maxSequenceNumber, fileNameBytes)
        return header + payload

    def __str__(self):
        return f"InitializePacket{{" \
               f"maxSequenceNumber={self.max_sequence_number}" \
               f", fileName={self.file_name}" \
               f", transmissionId={self.transmission_id}" \
               f", sequenceNumber={self.sequence_number}}}"
