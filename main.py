import sys
from Receiver import *

if len(sys.argv) != 6:
    print("Usage: python3 <transmission_id> <port> <target_folder> <ack_ip> <ack_port>")
    sys.exit(1)

transmission_id = int(sys.argv[1])
port = int(sys.argv[2])
target_folder = sys.argv[3]
if os.path.exists(target_folder) and not os.path.isdir(target_folder):
    print("Target folder can't be a file")
    sys.exit(1)
os.makedirs(target_folder, exist_ok=True)

ack_ip = sys.argv[4]
ack_port = int(sys.argv[5])

Receiver(transmission_id, port, target_folder, socket.gethostbyname(ack_ip), ack_port).start()
