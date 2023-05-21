from sequencer.OpenPacketSequence import *


class PacketSequencer:
    def __init__(self, maxOpenSequences: int, maxCachedPacketsPerSequence: int, continueSequence, cancelSequence):
        self.maxOpenSequences = maxOpenSequences
        self.maxCachedPacketsPerSequence = maxCachedPacketsPerSequence
        self.continueSequence = continueSequence
        self.cancelSequence = cancelSequence
        self.openSequences = {}

    def push(self, packet, transmissionId: int):
        try:
            sequence = self.openSequences.setdefault(transmissionId, OpenPacketSequence())
            sequence.cached_packets.append(packet)
            if len(sequence.cached_packets) > self.maxCachedPacketsPerSequence:
                del self.openSequences[transmissionId]
                self.cancelSequence(transmissionId)

            continue_sequence = self.continueSequence
            if not continue_sequence:
                del self.openSequences[transmissionId]
            else:
                sequence.next_sequence_number += 1
                cache = sequence.cached_packets
                if len(cache) > 0:
                    cache.sort(key=lambda p: p.getSequenceNumber())
                    while len(cache) > 0:
                        next_packet = cache.pop(0)
                        continue_sequence_now = self.continueSequence(transmissionId, next_packet)
                        if not continue_sequence_now:
                            cache.clear()
                            del self.openSequences[transmissionId]
                        else:
                            sequence.next_sequence_number += 1
        except Exception:
            self.cancelSequence(transmissionId)

        while len(self.openSequences) > self.maxOpenSequences:
            oldest_sequence_id = min(self.openSequences, key=lambda k: self.openSequences[k].opened_at)
            del self.openSequences[oldest_sequence_id]