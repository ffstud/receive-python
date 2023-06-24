import os
import traceback
import hashlib
import time
from packet.InitializePacket import *
from packet.FinalizePacket import *
from packet.DataPacket import *


class PacketDigest:
    def __init__(self, target_folder):
        self.target_folder = target_folder
        self.open_files = {}

    def continue_sequence(self, transmission_id, packet):
        if isinstance(packet, InitializePacket):
            return self.handle_init_packet(transmission_id, packet.getSequenceNumber(), packet)
        elif isinstance(packet, DataPacket):
            return self.handle_data_packet(transmission_id, packet)
        elif isinstance(packet, FinalizePacket):
            return self.handle_finalize_packet(transmission_id, packet)
        return True

    def handle_init_packet(self, transmission_id, seq_nr: int, packet: InitializePacket) -> bool:
        if seq_nr != 0:
            raise ValueError("sequence number invalid")
        if transmission_id in self.open_files:
            raise RuntimeError("File already opened")
        path = os.path.join(self.target_folder, packet.file_name)
        if os.path.exists(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        file = open(path, "ab")
        self.open_files[transmission_id] = (file, path)
        return True

    def handle_data_packet(self, transmission_id, data_packet: DataPacket) -> bool:
        if data_packet.sequence_number == 0:
            return False
        file_entry = self.open_files.get(transmission_id)
        if file_entry is None:
            raise RuntimeError("no such open file")
        try:
            file_entry[0].write(data_packet.data)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False
        return True

    def handle_finalize_packet(self, transmission_id, finalize_packet: FinalizePacket) -> bool:
        path = self.open_files[transmission_id][1]
        if self.open_files is None:
            raise RuntimeWarning("no such open file")
        try:
            self.open_files[transmission_id][0].close()
            hashShould = finalize_packet.getMd5()
            with open(path, "rb") as file:
                hashActual = hashlib.md5(file.read()).digest()

            if hashShould == hashActual:
                try:
                    file.close()
                except Exception as e:
                    print(e)
            else:
                print("Hashes do not match! Keeping corrupted file anyway!")
                print("Should: " + format(int.from_bytes(hashShould, byteorder='big'), '032x'))
                print("Actual: " + format(int.from_bytes(hashActual, byteorder='big'), '032x'))
        except Exception as ex:
            print(ex)

        self.open_files.pop(transmission_id)
        print("Processed finalize packet at: " + str(time.time() * 1000))
        print("File successfully transferred")

        return True

    def cancel_sequence(self, transmission_id):
        if self.open_files:
            del (self.open_files[transmission_id])
        else:
            FileNotFoundError("no such open file")
