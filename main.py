# a main entry file main.py (which is the only file called for execution)
import sys
from devices_new import Host, Router
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

    hostA = Host("Host A", HOST_A_IP, HOST_A_MAC, HOST_A_ROUTING_TABLE, HOST_A_ARP_TABLE)
    hostB = Host("Host B", HOST_B_IP, HOST_B_MAC, HOST_B_ROUTING_TABLE, HOST_B_ARP_TABLE)
    routerR1 = Router("Router R1", ROUTER_R1_ROUTING_TABLE, ROUTER_R1_ARP_TABLE)
    
    hostA.router = routerR1
    hostB.router = routerR1
    routerR1.hostA = hostA
    routerR1.hostB = hostB

    hostA.application_send(data, 5000, 80, HOST_B_IP)

if __name__ == "__main__":
    main()
    