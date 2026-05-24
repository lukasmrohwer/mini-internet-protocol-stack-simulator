from protocol import *
from config import *

class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
        """This function intialises the host based of the parameters it is given from main.py"""
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routingTable = routing_table       
        self.arpTable = arp_table               
        self.sequenceNumber = 0                 
        self.expectedSeqNum = 0                 
        self.waitingForAck = False              
        self.router = None    
        self.macTable = {}

        # creates protocol layers
        self.TransportLayer = TransportLayer(self)
        self.NetworkLayer = NetworkLayer(self)
        self.LinkLayer = LinkLayer(self)

    def application_send(self, data, src_port, dst_port, dst_ip):
        """This function simulates the application layer handing off data to the transport layer to initiate the chain."""
        self.TransportLayer.send(data, src_port, dst_port, dst_ip)

    def link_receive(self, frame):
        """This function simulates the host receiving data from the network."""
        self.LinkLayer.receive(frame)

class Router:
    def __init__(self, name, routing_table, arp_table):
        """This function intialises the router based of the parameters it is given from main.py"""
        self.name = name
        self.routingTable = routing_table       
        self.arpTable = arp_table               
        self.macTable = {}                      
        self.hostA = None                       
        self.hostB = None                       

        # defines the two interfaces on the router
        self.interfaces = {
            "Interface 1": {"ip": ROUTER_R1_INT1_IP, "mac": ROUTER_R1_INT1_MAC},
            "Interface 2": {"ip": ROUTER_R1_INT2_IP, "mac": ROUTER_R1_INT2_MAC},
        }

        # creates protocol layers
        self.NetworkLayer = NetworkLayer(self)
        self.LinkLayer = LinkLayer(self)

    def link_receive(self, frame, interface):
        """This function simulates the router receiving data from the network."""
        self.LinkLayer.receive(frame, interface)
