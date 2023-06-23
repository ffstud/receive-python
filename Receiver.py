import socket
from PacketDigest import *
from packet.AcknowledgementPacket import *
import time


class Receiver:
    def __init__(self, transmission_id, port, target_folder, ack_ip, ack_port, operating_mode):
        self.transmissionId = transmission_id
        self.transmissions = {}
        self.target_folder = target_folder
        self.digest = PacketDigest(target_folder)
        self.operating_mode = operating_mode
        # self.sequencer = PacketSequencer(128, 1024, self.digest.continue_sequence, self.digest.cancel_sequence)
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("", port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            print(e)
        self.ack_ip = ack_ip
        self.ack_port = ack_port

    @staticmethod
    def print_packet(packet):
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
                        print("Received finalize packet at:", time.time())
                        print(FinalizePacket.__str__(packet))
                    else:
                        packet = DataPacket(data)
                        packet.sequence_number = packet.sequence_number+1
                if self.digest.continue_sequence(transmission_id, packet):
                    if self.operating_mode == 1:
                        self.sendAcknowledgementPacket(transmission_id, sequence_number)
                else:
                    BaseException("Error while handling packet")
                    print(packet)
                    # print(packet)
            except UnicodeDecodeError as e:
                print(e)

    def sendAcknowledgementPacket(self, transmission_id, sequence_number):
        ackPaket = AcknowledgementPacket(transmission_id, sequence_number)
        byte = ackPaket.serialize()

        udp_packet = struct.pack("!%ds" % len(byte), byte)

        self.socket.sendto(udp_packet, (self.ack_ip, self.ack_port))
