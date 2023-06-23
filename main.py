import sys
from Receiver import *

def main():
    operating_mode = 0
    if len(sys.argv) > 1:
        operating_mode = int(sys.argv[1])

    if operating_mode == 0 and len(sys.argv) != 5:
        print("Usage: <operatingMode> <transmissionId> <port> <targetFolder>")
        return
    elif operating_mode == 1 and len(sys.argv) != 7:
        print("Usage: <operatingMode> <transmissionId> <port> <targetFolder> <ackIp> <ackPort>")
        return
    elif operating_mode == 2 and len(sys.argv)!= 8:
        print("Usage: <operatingMode> <transmissionId> <port> <targetFolder> <ackIp> <ackPort> <windowSize>")
        return


    transmission_id = int(sys.argv[2])
    port = int(sys.argv[3])
    target_folder = sys.argv[4]
    if os.path.exists(target_folder) and not os.path.isdir(target_folder):
        print("Target folder can't be a file")
        sys.exit(1)
    os.makedirs(target_folder, exist_ok=True)

    try:
        ack_ip = sys.argv[5]
    except IndexError:
        ack_ip = "127.0.0.1" #TODO: remove default case

    try:
        ack_port = int(sys.argv[6])
    except IndexError:
        ack_port = -1



    Receiver(transmission_id, port, target_folder, socket.gethostbyname(ack_ip), ack_port, operating_mode).start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
        sys.exit(0)
