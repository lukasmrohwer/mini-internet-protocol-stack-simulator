from protocol import Segment, Packet, Frame
from config import *

class Host:
    def __init__(self, name, ip, mac, routing_table, arp_table):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.routingTable = routing_table       # maps destination network -> {next_hop, interface}
        self.arpTable = arp_table               # maps next-hop IP -> MAC address
        self.sequenceNumber = 0                 # current seq number for sending (alternates 0/1)
        self.expectedSeqNum = 0                 # seq number we expect to receive next
        self.waitingForAck = False              # rdt2.2: are we waiting for an ACK right now?
        self.router = None    
        self.macTable = {}                  # reference to Router R1, set after creation in main.py

    # --- Application Layer Interface ---

    def application_send(self, data, src_port, dst_port, dst_ip):
        self.transport_send(data, src_port, dst_port, dst_ip)

    # --- Layer 4: Transport ---

    def transport_send(self, data, src_port, dst_port, dst_ip):
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(data)}")

        payloads = []
        i = 0
        
        while i < len(data):
            if len(data) > i + 500:
                payloads.append(data[i:i + 500])
            else:
                payloads.append(data[i:])
            i += 500
        
        for p in payloads:
            segment = Segment(src_port, dst_port, 0, self.sequenceNumber, p) 
            print(f"{self.name}: Layer 4: Checksum computed")
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.sequenceNumber}) (encapsulation)")

            self.waitingForAck = True

            while self.waitingForAck:
                print(f"{self.name}: Layer 4: Segment sent to Network Layer")
                self.network_send(segment, dst_ip)

            self.sequenceNumber = 1 - self.sequenceNumber

    def transport_receive(self, segment, src_ip):
        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if segment.verify_checksum() == False:
            print(f"{self.name}: Layer 4: Segment discarded due to Checksum error")
            return
        else:
            print(f"{self.name}: Layer 4: Checksum verified")

        if segment.type == 0:
            if segment.sequence_number == self.expectedSeqNum:
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                self.expectedSeqNum = 1 - self.expectedSeqNum

            ackSegment = Segment(None, None, 1, segment.sequence_number, "")
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ackSegment.sequence_number})")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
            self.network_send(ackSegment, src_ip)

        else:
            print(f"{self.name}: Layer 4: ACK received: seq={segment.sequence_number}")
            if segment.sequence_number == self.sequenceNumber:
                self.waitingForAck = False
            else:
                print(f"{self.name}: Layer 4: Segment retransmitted due to incorrect ACK")
        
    # --- Layer 3: Network ---

    def network_send(self, segment, dst_ip):
        dstArr = dst_ip.split(".")[:3]
        dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])
        route = self.routingTable[dstPrefix]

        if route["next_hop"] != None:
            nextHop = route["next_hop"]
        else:
            nextHop = dst_ip

        interface = route["interface"]

        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL=100")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {nextHop}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        totalLength = segment.length + 12 
        packet = Packet(self.ip, dst_ip, 100, 17, totalLength, segment)

        self.link_send(packet, nextHop, interface)
        
    def network_receive(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if packet.dst_ip == self.ip:
            print(f"{self.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
            self.transport_receive(packet.payload, packet.src_ip)

    # --- Layer 2: Data Link ---

    def link_send(self, packet, nextHop, outInterface):
        dstMac = self.arpTable[nextHop]

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({nextHop}) → {dstMac}")

        frame = Frame(self.mac, dstMac, "0x0800", packet.total_length, packet)

        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dstMac}")
        print(f"{self.name}: Layer 2: Frame sent")

        self.router.link_receive(frame, outInterface)

    def link_receive(self, frame):
        print(f"{self.name}: Layer 2: Frame received")

        self.macTable[frame.src_mac] = True

        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")
        print(f"{self.name}: Layer 2: Packet delievered to Network Layer")

        self.network_receive(frame.payload)


class Router:
    def __init__(self, name, routing_table, arp_table):
        self.name = name
        self.routingTable = routing_table       # maps destination network -> {next_hop, interface}
        self.arpTable = arp_table               # maps next-hop IP -> MAC address
        self.macTable = {}                      # learned MACs: {mac_address: interface} (starts empty)
        self.hostA = None                       # reference to Host A, set after creation in main.py
        self.hostB = None                       # reference to Host B, set after creation in main.py

        # Each interface has its own IP and MAC
        self.interfaces = {
            "Interface 1": {"ip": ROUTER_R1_INT1_IP, "mac": ROUTER_R1_INT1_MAC},
            "Interface 2": {"ip": ROUTER_R1_INT2_IP, "mac": ROUTER_R1_INT2_MAC},
        }

    # --- Layer 2: Data Link ---

    def link_receive(self, frame, interface):
        # Receives a Frame on a given interface
        # Logs receipt, learns source MAC, strips frame, passes payload to network_receive
        pass

    def link_send(self, packet, next_hop_ip, out_interface):
        # Looks up next_hop_ip in arp_table to get destination MAC
        # Uses out_interface to pick the correct source MAC
        # Wraps packet in a Frame, hands frame to the correct host (host_a or host_b)
        pass

    # --- Layer 3: Network ---

    def network_receive(self, packet):
        # Receives a Packet from link_receive
        # Logs receipt, reads destination IP, decrements TTL (drops if 0)
        # Looks up routing table to find next_hop and out_interface
        # Passes packet down to link_send
        pass
