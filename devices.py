from protocol import TransportLayer
from protocol import *
from config import *

class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
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

        self.TransportLayer = TransportLayer(self)
        self.NetworkLayer = NetworkLayer(self)
        self.LinkLayer = LinkLayer(self)

    def application_send(self, data, src_port, dst_port, dst_ip):
        self.TransportLayer.send(data, src_port, dst_port, dst_ip)

    def link_receive(self, frame):
        self.LinkLayer.receive(frame)

class Router:
    def __init__(self, name, routing_table, arp_table):
        self.name = name
        self.routingTable = routing_table       
        self.arpTable = arp_table               
        self.macTable = {}                      
        self.hostA = None                       
        self.hostB = None                       

        self.interfaces = {
            "Interface 1": {"ip": ROUTER_R1_INT1_IP, "mac": ROUTER_R1_INT1_MAC},
            "Interface 2": {"ip": ROUTER_R1_INT2_IP, "mac": ROUTER_R1_INT2_MAC},
        }

        self.NetworkLayer = NetworkLayer(self)
        self.LinkLayer = LinkLayer(self)

    def link_receive(self, frame, interface):
        self.LinkLayer.receive(frame, interface)
