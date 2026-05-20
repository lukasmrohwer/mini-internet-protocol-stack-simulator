from protocol import Segment, Packet, Frame
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
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        self.network_receive(frame.payload)


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

    # --- Layer 2: Data Link ---

    def link_receive(self, frame, interface):
        print(f"{self.name}: Layer 2: Frame received on {interface}")

        self.macTable[frame.src_mac] = interface

        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac} on {interface}")
        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        self.network_receive(frame.payload)

    def link_send(self, packet, nextHop, outInterface):
        dstMac = self.arpTable[nextHop] 
        srcMac = self.interfaces[outInterface]["mac"]

        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({nextHop}) → {dstMac}")
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={srcMac}, DST_MAC={dstMac}")
        print(f"{self.name}: Layer 2: Frame forwarded on {outInterface}")

        frame = Frame(srcMac, dstMac, "0x0800", packet.total_length, packet)

        if outInterface == "Interface 1":
            self.hostA.link_receive(frame)
        else:
            self.hostB.link_receive(frame)

    # --- Layer 3: Network ---

    def network_receive(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        oldTtl = packet.ttl
        packet.ttl -= 1

        if packet.ttl == 0:
            print(f"{self.name}: Layer 3: TTL hit 0")
            return
        
        print(f"{self.name}: Layer 3: TTL decremented: {oldTtl} → {packet.ttl}")

        dstArr = packet.dst_ip.split(".")[:3]
        dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])

        route = self.routingTable[dstPrefix]

        if route["next_hop"] != None:
            nextHop = route["next_hop"]
        else:
            nextHop = packet.dst_ip

        interface = route["interface"]

        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {nextHop}")
        print(f"{self.name}: Layer 3: Outgoing interface selected ({interface})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        self.link_send(packet, nextHop, interface)
