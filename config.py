# ip and mac addresses for the hosts and router interfaces
HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"

HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

ROUTER_R1_INT1_IP = "10.0.1.1"
ROUTER_R1_INT2_IP = "10.0.2.1"

ROUTER_R1_INT1_MAC = "BB:BB:BB:BB:BB:BB"
ROUTER_R1_INT2_MAC = "CC:CC:CC:CC:CC:CC"

# routing and arp tables for the hosts and router
HOST_A_ROUTING_TABLE = {
    "10.0.1": {"next_hop": None, "interface": "Interface 1"},
    "10.0.2": {"next_hop": "10.0.1.1", "interface": "Interface 1"},
}

HOST_B_ROUTING_TABLE = {
    "10.0.2": {"next_hop": None, "interface": "Interface 2"},
    "10.0.1": {"next_hop": "10.0.2.1", "interface": "Interface 2"},
}

ROUTER_R1_ROUTING_TABLE = {
    "10.0.1": {"next_hop": None, "interface": "Interface 1"},
    "10.0.2": {"next_hop": None, "interface": "Interface 2"},
}

HOST_A_ARP_TABLE = {
    "10.0.1.1": "BB:BB:BB:BB:BB:BB",
}

HOST_B_ARP_TABLE = {
    "10.0.2.1": "CC:CC:CC:CC:CC:CC",
}

ROUTER_R1_ARP_TABLE = {
    "10.0.1.10": "AA:AA:AA:AA:AA:AA",
    "10.0.2.20": "DD:DD:DD:DD:DD:DD",
}