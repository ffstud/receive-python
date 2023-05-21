import time


class OpenPacketSequence:
    def __init__(self):
        self.opened_at = int(
            time.time() * 1000)  # Stores the system time (in milliseconds) when the packet sequence was opened
        self.cached_packets = []  # An empty list of cached packets received so far in the packet sequence
        self.next_sequence_number = 0  # The expected sequence number of the next packet in the sequence
