import socket
from PacketDigest import *
from packet.AcknowledgementPacket import *
import time


class Receiver:
    def __init__(self, transmission_id, port, target_folder, ack_ip, ack_port, operating_mode, window_size, window_timeout, duplicate_ack_delay):
        self.transmissionId = transmission_id
        self.transmissions = {}
        self.target_folder = target_folder
        self.digest = PacketDigest(target_folder)
        self.operating_mode = operating_mode
        self.window_timeout = window_timeout
        self.duplicate_ack_delay = duplicate_ack_delay
        self.window_start = 0
        self.retransmitted_packets = 0
        self.window_buffer = []
        self.missing_packets = []
        self.window_size = window_size

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("", port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            print(e)
        self.ack_ip = ack_ip
        self.ack_port = ack_port

    def has_finalize_packet(self, list):
        return any(isinstance(packet, FinalizePacket) for packet in list)

    def has_packet_with_sequence_number(self, list, sequence_number):
        return any(packet.sequence_number == sequence_number for packet in list)
    @staticmethod
    def print_packet(packet):
        print("Received packet:")
        print(packet)

    def start(self):
        global data
        buffer_size = 65535
        while True:
            try:
                try:
                    data, addr = self.socket.recvfrom(buffer_size)
                except TimeoutError as e:
                    #transmission of window is complete
                    if self.operating_mode == 2:
                        # check if window is ready for processing and is filled or is last window
                        if (not self.missing_packets) and (len(
                                self.window_buffer) == self.window_size or self.has_finalize_packet(self.window_buffer) and len(self.window_buffer) == self.transmissions.get(
                                    self.transmissionId) - self.window_start + 2):
                            self.process_window()
                        else:
                            self.check_for_missing_packets()

                            self.request_missing_packet(self.missing_packets.pop())
                        continue
                    else:
                        print("Socket timed out!")


                sequence_number = PacketInterpreter.getSequenceNumber(data)

                transmission_id = PacketInterpreter.getTransmissionId(data)

                if PacketInterpreter.isInitializationPacket(data):
                    packet = InitializePacket(data, len(data))
                    max_sequence_number = packet.getMaxSequenceNumber()

                    self.transmissions[transmission_id] = max_sequence_number

                    print("Received initialization packet at:", time.time())
                    print(InitializePacket.__str__(packet))
                    # set timeout for socket in sliding window mode, since we have to recognize
                    # that the transmitter is finished with sending a window
                    if self.operating_mode == 2:
                        self.socket.settimeout(self.window_timeout/100)
                else:
                    # no initialization packet seen before for this transmissionId -> abort transmission
                    if transmission_id not in self.transmissions:
                        print("Did not receive initialization packet before, abort transmission")
                        break
                    # check for finalize or data packet
                    if sequence_number == (self.transmissions[transmission_id] + 1):
                        packet = FinalizePacket(data, len(data))
                        print("Received finalize packet at:", time.time())
                        print(FinalizePacket.__str__(packet))
                    else:
                        packet = DataPacket(data)
                if self.operating_mode != 2:
                    if self.digest.continue_sequence(transmission_id, packet):
                        if self.operating_mode == 1:
                            self.sendAcknowledgementPacket(transmission_id, sequence_number)
                    else:
                        BaseException("Error while handling packet")
                        print(packet)
                        # print(packet)
                else:
                    self.window_buffer.append(packet)
            except UnicodeDecodeError as e:
                print(e)

    def sendAcknowledgementPacket(self, transmission_id, sequence_number):
        ackPaket = AcknowledgementPacket(transmission_id, sequence_number)

        byte = ackPaket.serialize()
        udp_packet = struct.pack("!%ds" % len(byte), byte)
        self.socket.sendto(udp_packet, (self.ack_ip, self.ack_port))

    def process_window(self):
        self.window_buffer.sort(key=lambda packet: packet.sequence_number)
        lastPacket = self.window_buffer.__getitem__(len(self.window_buffer)-1)
        if isinstance(lastPacket, Packet):
            self.sendAcknowledgementPacket(self.transmissionId, lastPacket.getSequenceNumber())
            for window_packet in self.window_buffer:
                if isinstance(window_packet, Packet):
                    if not self.digest.continue_sequence(self.transmissionId, window_packet):
                        print(f"Error while handling packet: {window_packet} ")
            self.window_start += self.window_size

            if any(isinstance(packet, FinalizePacket) for packet in self.window_buffer):
                print(f"Number of retransmitted packets: {self.retransmitted_packets}")
                self.socket.settimeout(None)  # reset timeout since no transmission is active
                self.window_start = 0
                self.retransmitted_packets = 0

            self.window_buffer.clear()

    def check_for_missing_packets(self):
        # first check if window is not complete
        if len(self.window_buffer) != self.window_size:
            self.window_buffer.sort(key=lambda packet: packet.getSequenceNumber())
            # add missing sequence numbers
            if self.window_start + self.window_size > self.transmissions.get(
                    self.transmissionId):  # last window in range
                range_limit = self.transmissions.get(self.transmissionId) + 2
            else:
                range_limit = self.window_start + self.window_size  # there is still another full window

            for i in range(self.window_start, range_limit):  # corrected range to range_limit
                if not self.has_packet_with_sequence_number(self.window_buffer, i) and i not in self.missing_packets:
                    self.missing_packets.append(i)

    def request_missing_packet(self, sequence_number):
        self.sendAcknowledgementPacket(self.transmissionId, sequence_number)
        time.sleep(self.duplicate_ack_delay / 1000)
        self.sendAcknowledgementPacket(self.transmissionId, sequence_number)
        time.sleep(self.duplicate_ack_delay / 1000)

        self.retransmitted_packets += 1
