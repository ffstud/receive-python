
class PacketInterpreter:
    @staticmethod
    def isInitializationPacket(udpPacket):
        return PacketInterpreter.getSequenceNumber(udpPacket) == 0

    @staticmethod
    def getSequenceNumber(data):
        return int.from_bytes(data[2:6], byteorder='big', signed=True)

    @staticmethod
    def getTransmissionId(data):
        return int.from_bytes(data[0:2], byteorder='big', signed=True)

    @staticmethod
    def getUIntAt(data, index):
        return int.from_bytes(data[index:index+4], byteorder='big')
    @staticmethod
    def getStringAt(data, index, length):
        return data[index:index+length].decode('utf-8')

    @staticmethod
    def getByteArrayAt(data, index, length):
        return data[index:index+length]
