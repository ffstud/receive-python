import os
import traceback
import hashlib
from src.packet.InitializePacket import *
from src.packet.FinalizePacket import *
from src.packet.DataPacket import *


class PacketDigest:
    def __init__(self, targetFolder):
        self.targetFolder = targetFolder
        self.openFiles = {}

    def continueSequence(self, transmissionId, packet):
        if isinstance(packet, InitializePacket):
            return self.handle_init_packet(transmissionId, packet.getSequenceNumber(), packet)
        elif isinstance(packet, DataPacket):
            return self.handle_data_packet(transmissionId, packet)
        elif isinstance(packet, FinalizePacket):
            return self.handle_finalize_packet(transmissionId, packet)
        return False

    def handle_init_packet(self, transmission_id, seq_nr: int, packet: InitializePacket) -> bool:
        if seq_nr != 0:
            raise ValueError("sequence number invalid")
        if transmission_id in self.openFiles:
            raise RuntimeError("File already opened")
        path = os.path.join(self.targetFolder, packet.file_name)
        if os.path.exists(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        file = open(path, "ab")
        self.openFiles[transmission_id] = (file, path)

        return True

    def handle_data_packet(self, transmission_id, data_packet: DataPacket) -> bool:
        if data_packet.sequence_number == 0:
            return False
        fileEntry = self.openFiles.get(transmission_id)
        if fileEntry is None:
            raise RuntimeError("no such open file")
        try:
            fileEntry[0].write(data_packet.data)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False
        return True

    def handle_finalize_packet(self, transmission_id, finalize_packet: FinalizePacket) -> bool:
        path = self.openFiles[transmission_id][1]
        if self.openFiles is None:
            raise RuntimeWarning("no such open file")
        try:
            self.openFiles[transmission_id][0].close()
            hashShould = finalize_packet.getMd5()
            with open(path, "rb") as file:
                hashActual = hashlib.md5(file.read()).digest()

            if hashShould == hashActual:
                print("File successfully transferred")
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

        return False

    def cancelSequence(self, transmission_id):
        if self.openFiles:
            del (self.openFiles[transmission_id])
        else:
            FileNotFoundError("no such open file")
