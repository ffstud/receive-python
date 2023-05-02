import time


class OpenPacketSequence:
    def __init__(self):
        self.openedAt = int(
            time.time() * 1000)  # Stores the system time (in milliseconds) when the packet sequence was opened
        self.cachedPackets = []  # An empty list of cached packets received so far in the packet sequence
        self.nextSequenceNumber = 0  # The expected sequence number of the next packet in the sequence
