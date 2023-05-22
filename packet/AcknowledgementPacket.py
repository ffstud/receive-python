from packet.Packet import *


class AcknowledgementPacket(Packet):
    def __init__(self, transmissionId, sequenceNumber):
        super().__init__(transmissionId, sequenceNumber)

    def serialize(self):
        return super().serialize()

    def __str__(self):
        return f"AcknowledgementPacket{{" \
               f"transmissionId={self.transmission_id}, " \
               f"sequenceNumber={self.sequence_number}}}"
