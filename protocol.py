class Segment:
    def __init__(self, src_port, dst_port, type, sequence_number, data, checksum):
        """This function initialises a transport layer segment (UDP-like) with header fields and payload."""
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = len(data) + 8  # payload length plus 8-byte header
        self.checksum = checksum
        self.type = type              # 0 = DATA, 1 = ACK
        self.sequence_number = sequence_number
        self.data = data

class Packet:
    def __init__(self, src_ip, dst_ip, ttl, protocol, total_length, payload):
        """This function initialises a network layer packet (IP-like) with header fields and a segment as payload."""
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl                # time-to-live, decremented at each router hop
        self.protocol = protocol      # 17 = UDP
        self.total_length = total_length
        self.payload = payload

class Frame:
    def __init__(self, src_mac, dst_mac, type, length, payload):
        """This function initialises a data link layer frame (Ethernet-like) with header fields and a packet as payload."""
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.type = type              # EtherType, e.g. 0x0800 for IPv4
        self.payload = payload

class Layer:
    def __init__(self, node):
        """This function initialises a generic protocol layer and stores a reference to the owning node."""
        self.node = node

class TransportLayer(Layer):

    def segment_data(self, data):
        """This function splits data into chunks of at most 500 bytes to fit within a single segment payload."""
        payloads = []
        i = 0w

        while i < len(data):
            if len(data) > i + 500:
                payloads.append(data[i:i + 500])
            else:
                payloads.append(data[i:])
            i += 500

        return payloads

    def calculate_checksum(self, data):
        """
        This function calculates the UDP checksum for the data given the algorithm specified in Week 8's lecture slides.
        """
        # Convert string to bytes (handles standard ASCII/UTF-8 encoding)
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # Pad with a zero byte if the length is odd to make even 16-bit words
        if len(data) % 2 != 0:
            data += b'\x00'

        total = 0
        
        # Treat segment contents as a sequence of 16-bit integers
        for i in range(0, len(data), 2):
            # Shift the first byte 8 bits left, add the second byte (Big-Endian)
            word = (data[i] << 8) + data[i+1]
            total += word

        # Handle carryout wraparound
        # Add any overflow beyond 16 bits back into the sum
        while (total >> 16) > 0:
            total = (total & 0xFFFF) + (total >> 16)

        # Take the 1s complement of the sum and mask to 16 bits
        checksum = ~total & 0xFFFF

        return checksum

    def verify_checksum(self, segment):
        """This function returns True if the segment's checksum matches a freshly computed checksum of its data."""
        if self.calculate_checksum(segment.data) == segment.checksum:
            return True
        return False

    def create_segment(self, src_port, dst_port, type, sequence_number, data, checksum):
        """This function constructs and returns a new Segment object with the given header fields and payload."""
        return Segment(src_port, dst_port, type, sequence_number, data, checksum)

    def send(self, data, src_port, dst_port, dst_ip):
        """This function segments the data and sends each segment to the Network Layer, retransmitting until an ACK is received (Stop-and-Wait)."""
        print(f"{self.node.name}: Layer 4: Data received from Application Layer. Data size={len(data)}")

        payloads = self.segment_data(data)

        for p in payloads:
            checksum = self.calculate_checksum(p)
            print(f"{self.node.name}: Layer 4: Checksum computed")

            segment = self.create_segment(src_port, dst_port, 0, self.node.sequenceNumber, p, checksum)
            print(f"{self.node.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={segment.sequence_number}) (encapsulation)")

            self.node.waitingForAck = True

            # retransmit the segment until the correct ACK is received
            while self.node.waitingForAck:
                print(f"{self.node.name}: Layer 4: Segment sent to Network Layer")
                self.node.NetworkLayer.send(segment, dst_ip)

            # alternate sequence number between 0 and 1 (alternating bit protocol)
            self.node.sequenceNumber = 1 - self.node.sequenceNumber

    def receive(self, segment, src_ip):
        """This function processes an incoming segment, verifies its checksum, delivers data to the application, and sends an ACK back."""
        print(f"{self.node.name}: Layer 4: Segment received from Network Layer")

        if self.verify_checksum(segment) == False:
            print(f"{self.node.name}: Layer 4: Segment discarded due to Checksum error")
            return
        else:
            print(f"{self.node.name}: Layer 4: Checksum verified")

        if segment.type == 0:
            # deliver in-order DATA segments to the application layer
            if segment.sequence_number == self.node.expectedSeqNum:
                print(f"{self.node.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                self.node.expectedSeqNum = 1 - self.node.expectedSeqNum

            # always send an ACK for the received sequence number
            ackChecksum = self.calculate_checksum("")
            ackSegment = Segment(None, None, 1, segment.sequence_number, "", ackChecksum)
            print(f"{self.node.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ackSegment.sequence_number})")
            print(f"{self.node.name}: Layer 4: Segment sent to Network Layer")
            self.node.NetworkLayer.send(ackSegment, src_ip)

        else:
            # ACK received — check whether it matches the segment we were waiting on
            print(f"{self.node.name}: Layer 4: ACK received: seq={segment.sequence_number}")
            if segment.sequence_number == self.node.sequenceNumber:
                self.node.waitingForAck = False
            else:
                print(f"{self.node.name}: Layer 4: Segment retransmitted due to incorrect ACK")

class NetworkLayer(Layer):

    def send(self, segment, dst_ip):
        """This function wraps a segment in a packet and forwards it to the Link Layer based on a routing table lookup."""
        # extract the /24 prefix to use as the routing table key
        dstArr = dst_ip.split(".")[:3]
        dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])
        route = self.node.routingTable[dstPrefix]

        if route["next_hop"] != None:
            nextHop = route["next_hop"]
        else:
            nextHop = dst_ip     # destination is on the local subnet; send directly

        interface = route["interface"]

        print(f"{self.node.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.node.ip}, DST_IP={dst_ip}, TTL=100")
        print(f"{self.node.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.node.name}: Layer 3: Routing table lookup performed")
        print(f"{self.node.name}: Layer 3: Next-hop IP determined: {nextHop}")
        print(f"{self.node.name}: Layer 3: Outgoing interface selected")
        print(f"{self.node.name}: Layer 3: Packet forwarded to Data Link Layer")

        totalLength = segment.length + 12   # segment length plus 12-byte IP header
        packet = Packet(self.node.ip, dst_ip, 100, 17, totalLength, segment)

        self.node.LinkLayer.send(packet, nextHop, interface)

    def receive(self, packet):
        """This function processes an incoming packet, delivering it locally or forwarding it after decrementing TTL."""
        print(f"{self.node.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
        print(f"{self.node.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if hasattr(self.node, "ip") and packet.dst_ip == self.node.ip:
            # packet has reached its destination — hand payload up to Transport Layer
            print(f"{self.node.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.node.name}: Layer 3: Segment delivered to Transport Layer")
            self.node.TransportLayer.receive(packet.payload, packet.src_ip)
        else:
            oldTtl = packet.ttl
            packet.ttl -= 1

            if packet.ttl == 0:
                # discard packet to prevent infinite loops in the network
                print(f"{self.node.name}: Layer 3: TTL hit 0")
                return

            print(f"{self.node.name}: Layer 3: TTL decremented: {oldTtl} → {packet.ttl}")

            # look up the next hop for the destination prefix
            dstArr = packet.dst_ip.split(".")[:3]
            dstPrefix = str(dstArr[0]) + "." + str(dstArr[1]) + "." + str(dstArr[2])

            route = self.node.routingTable[dstPrefix]

            if route["next_hop"] != None:
                nextHop = route["next_hop"]
            else:
                nextHop = packet.dst_ip  # destination is on the local subnet; send directly

            interface = route["interface"]

            print(f"{self.node.name}: Layer 3: Routing table lookup performed")
            print(f"{self.node.name}: Layer 3: Next-hop IP determined: {nextHop}")
            print(f"{self.node.name}: Layer 3: Outgoing interface selected ({interface})")
            print(f"{self.node.name}: Layer 3: Packet forwarded to Data Link Layer")

            self.node.LinkLayer.send(packet, nextHop, interface)

class LinkLayer(Layer):

    def send(self, packet, nextHop, outInterface):
        """This function wraps a packet in a frame and delivers it directly to the next device's link_receive method."""
        # look up the destination MAC address for the next-hop IP in the ARP table
        dstMac = self.node.arpTable[nextHop]

        # routers have per-interface MACs; hosts have a single MAC
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

        # deliver the frame directly to the connected device (simulates the physical link)
        if hasattr(self.node, "interfaces"):
            if outInterface == "Interface 1":
                self.node.hostA.link_receive(frame)
            else:
                self.node.hostB.link_receive(frame)
        else:
            self.node.router.link_receive(frame, outInterface)

    def receive(self, frame, interface=None):
        """This function accepts an incoming frame, learns the source MAC, and passes the payload up to the Network Layer."""
        if interface: 
            # router path — record which interface the source MAC arrived on
            print(f"{self.node.name}: Layer 2: Frame received on {interface}")
            self.node.macTable[frame.src_mac] = interface
            print(f"{self.node.name}: Layer 2: Source MAC learned: {frame.src_mac} on {interface}")
        else:
            # host path — simply record that the MAC is reachable
            print(f"{self.node.name}: Layer 2: Frame received")
            self.node.macTable[frame.src_mac] = True
            print(f"{self.node.name}: Layer 2: Source MAC learned: {frame.src_mac}")

        print(f"{self.node.name}: Layer 2: Packet delivered to Network Layer")
        self.node.NetworkLayer.receive(frame.payload)