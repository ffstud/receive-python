import os
import sys
from Receiver import *

if len(sys.argv) != 3:
    print("Usage: <targetFolder> <port>")
    sys.exit(1)

target_folder = sys.argv[1]
if os.path.exists(target_folder) and not os.path.isdir(target_folder):
    print("Target folder can't be a file")
    sys.exit(1)
os.makedirs(target_folder, exist_ok=True)

port = int(sys.argv[2])
Receiver(target_folder, port).start()
