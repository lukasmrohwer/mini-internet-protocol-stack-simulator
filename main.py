# a main entry file main.py (which is the only file called for execution)
import sys
from devices import Host, Router
from config import *

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size>")
        sys.exit(1)

    try:
        msg_size = int(sys.argv[1])
    except ValueError:
        print("Message size must be an integer.")
        sys.exit(1)

    data = "X" * msg_size

    host_a = Host("Host A", HOST_A_IP, HOST_A_MAC)
    host_b = Host("Host B", HOST_B_IP, HOST_B_MAC)
    router_r1 = Router("Router R1")

    host_a.application_send(data, 5000, 80)

if __name__ == "__main__":
    main()
    