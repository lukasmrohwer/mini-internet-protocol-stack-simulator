# a protocol.py file containing the header definitions and classes for Layers 2, 3, and 4

class Segment:
    def __init__(self, src_port, dst_port, type, sequence_number, data, checksum):
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = len(data) + 8
        self.checksum = checksum
        self.type = type
        self.sequence_number = sequence_number
        self.data = data
    
class Packet:
    def __init__(self, src_ip, dst_ip, ttl, protocol, total_length, payload):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.total_length = total_length
        self.payload = payload

class Frame:
    def __init__(self, src_mac, dst_mac, type, length, payload):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.type = type
        self.payload = payload


class Layer:
    def __init__(self, node):
        self.node = node

class TransportLayer(Layer):

    def segment_data(self, data):
        payloads = []
        i = 0

        while i < len(data):
            if len(data) > i + 500:
                payloads.append(data[i:i + 500])
            else:
                payloads.append(data[i:])
            i += 500
        
        return payloads

    def calculate_checksum(self, data):
        total = 0
        for c in data:
            total += ord(c)

        return (total % 65536)

    def verify_checksum(self, segment):
        if self.calculate_checksum(segment.data) == segment.checksum:
            return True
        return False        

    def create_segment(self, src_port, dst_port, type, sequence_number, data, checksum):
        return Segment(src_port, dst_port, type, sequence_number, data, checksum)

    def send(self, data, src_port, dst_port, dst_ip):
        print(f"{self.node.name}: Layer 4: Data received from Application Layer. Data size={len(data)}")

        payloads = self.segment_data(data)

        for p in payloads:
            checksum = self.calculate_checksum(p)
            print(f"{self.node.name}: Layer 4: Checksum computed")

            segment = self.create_segment(src_port, dst_port, 0, self.node.sequenceNumber, p, checksum) 
            print(f"{self.node.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={segment.sequence_number}) (encapsulation)")

            self.node.waitingForAck = True

            while self.node.waitingForAck:
                print(f"{self.node.name}: Layer 4: Segment sent to Network Layer")
                self.node.NetworkLayer.send(segment, dst_ip)

            self.node.sequenceNumber = 1 - self.node.sequenceNumber

    def receive(self, segment, src_ip):
        print(f"{self.node.name}: Layer 4: Segment received from Network Layer")

        if self.verify_checksum(segment) == False:
            print(f"{self.node.name}: Layer 4: Segment discarded due to Checksum error")
            return
        else:
            print(f"{self.node.name}: Layer 4: Checksum verified")

        if segment.type == 0:
            if segment.sequence_number == self.node.expectedSeqNum:
                print(f"{self.node.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                self.node.expectedSeqNum = 1 - self.node.expectedSeqNum

            ackChecksum = self.calculate_checksum("")
            ackSegment = Segment(None, None, 1, segment.sequence_number, "", ackChecksum)
            print(f"{self.node.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ackSegment.sequence_number})")
            print(f"{self.node.name}: Layer 4: Segment sent to Network Layer")
            self.node.NetworkLayer.send(ackSegment, src_ip)

        else:
            print(f"{self.node.name}: Layer 4: ACK received: seq={segment.sequence_number}")
            if segment.sequence_number == self.node.sequenceNumber:
                self.node.waitingForAck = False
            else:
                print(f"{self.node.name}: Layer 4: Segment retransmitted due to incorrect ACK")

class NetworkLayer(Layer):

    def send(self, segment, dst_ip):
        dstArr = dst_ip.split(".")[:3]
        dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])
        route = self.node.routingTable[dstPrefix]

        if route["next_hop"] != None:
            nextHop = route["next_hop"]
        else:
            nextHop = dst_ip

        interface = route["interface"]

        print(f"{self.node.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.node.ip}, DST_IP={dst_ip}, TTL=100")
        print(f"{self.node.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.node.name}: Layer 3: Routing table lookup performed")
        print(f"{self.node.name}: Layer 3: Next-hop IP determined: {nextHop}")
        print(f"{self.node.name}: Layer 3: Outgoing interface selected")
        print(f"{self.node.name}: Layer 3: Packet forwarded to Data Link Layer")

        totalLength = segment.length + 12 
        packet = Packet(self.node.ip, dst_ip, 100, 17, totalLength, segment)

        self.node.LinkLayer.send(packet, nextHop, interface)

    def receive(self, packet):
        print(f"{self.node.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.node.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if hasattr(self.node, "ip") and packet.dst_ip == self.node.ip:
            print(f"{self.node.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.node.name}: Layer 3: Segment delivered to Transport Layer")
            self.node.TransportLayer.receive(packet.payload, packet.src_ip)
        else:
            oldTtl = packet.ttl
            packet.ttl -= 1

            if packet.ttl == 0:
                print(f"{self.node.name}: Layer 3: TTL hit 0")
                return
            
            print(f"{self.node.name}: Layer 3: TTL decremented: {oldTtl} → {packet.ttl}")

            dstArr = packet.dst_ip.split(".")[:3]
            dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])

            route = self.node.routingTable[dstPrefix]

            if route["next_hop"] != None:
                nextHop = route["next_hop"]
            else:
                nextHop = packet.dst_ip

            interface = route["interface"]

            print(f"{self.node.name}: Layer 3: Routing table lookup performed")
            print(f"{self.node.name}: Layer 3: Next-hop IP determined: {nextHop}")
            print(f"{self.node.name}: Layer 3: Outgoing interface selected ({interface})")
            print(f"{self.node.name}: Layer 3: Packet forwarded to Data Link Layer")

            self.node.LinkLayer.send(packet, nextHop, interface)

class LinkLayer(Layer):
    
    def send(self, packet, nextHop, outInterface):
        dstMac = self.node.arpTable[nextHop]
        
        if hasattr(self.node, "interfaces"):
            srcMac = self.node.interfaces[outInterface]["mac"]
        else:
            srcMac = self.node.mac

        print(f"{self.node.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.node.name}: Layer 2: Destination MAC lookup for next-hop IP ({nextHop}) → {dstMac}")
        print(f"{self.node.name}: Layer 2: Frame created: SRC_MAC={srcMac}, DST_MAC={dstMac}")
        
        if hasattr(self.node, "interfaces"):
            print(f"{self.node.name}: Layer 2: Frame forwarded on {outInterface}")
        else:
            print(f"{self.node.name}: Layer 2: Frame sent")

        frame = Frame(srcMac, dstMac, "0x0800", packet.total_length, packet)

        if hasattr(self.node, "interfaces"):
            if outInterface == "Interface 1":
                self.node.hostA.link_receive(frame)
            else:
                self.node.hostB.link_receive(frame)
        else:
            self.node.router.link_receive(frame, outInterface)

    def receive(self, frame, interface=None):
        if interface:
            print(f"{self.node.name}: Layer 2: Frame received on {interface}")
            self.node.macTable[frame.src_mac] = interface
            print(f"{self.node.name}: Layer 2: Source MAC learned: {frame.src_mac} on {interface}")
        else:
            print(f"{self.node.name}: Layer 2: Frame received")
            self.node.macTable[frame.src_mac] = True
            print(f"{self.node.name}: Layer 2: Source MAC learned: {frame.src_mac}")
            
        print(f"{self.node.name}: Layer 2: Packet delivered to Network Layer")
        self.node.NetworkLayer.receive(frame.payload)