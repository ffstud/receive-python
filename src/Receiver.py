import socket
from src.PacketDigest import *
from src.sequencer.PacketSequence import *
import time


class Receiver:
    def __init__(self, dropOffFolder, port):
        self.transmissions = {}
        self.digest = PacketDigest(dropOffFolder)
        self.dropOffFolder = dropOffFolder
        self.sequencer = PacketSequencer(128, 1024, self.digest.continueSequence, self.digest.cancelSequence)
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("", port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            print(e)

    def print_packet(self, packet):
        print("Received packet:")
        print(packet)

    def start(self):
        global data
        buffer_size = 65535
        while True:
            try:
                data, addr = self.socket.recvfrom(buffer_size)

                sequence_number = PacketInterpreter.getSequenceNumber(data)
                transmission_id = PacketInterpreter.getTransmissionId(data)

                if PacketInterpreter.isInitializationPacket(data):
                    packet = InitializePacket(data, len(data))
                    max_sequence_number = packet.getMaxSequenceNumber()

                    self.transmissions[transmission_id] = max_sequence_number
                    self.sequencer.push(packet, transmission_id)

                    print("Received initialization packet at:", time.time())
                    print(InitializePacket.__str__(packet))
                else:
                    # no initialization packet seen before for this transmissionId -> abort transmission
                    if transmission_id not in self.transmissions:
                        print("Did not receive initialization packet before, abort transmission")
                        break
                # check for finalize or data packet
                if sequence_number == (self.transmissions[transmission_id] + 1):
                    print("This is the self.transmissions[transmission_id] of the Term: " + str(self.transmissions))
                    packet = FinalizePacket(data, len(data))
                    self.sequencer.push(packet, transmission_id)
                    print("Received finalize packet at:", time.time())

                    print(FinalizePacket.__str__(packet))
                else:
                    packet = DataPacket(data)
                    self.sequencer.push(packet, transmission_id)
                    print(packet)
            except UnicodeDecodeError as e:
                print(e)

