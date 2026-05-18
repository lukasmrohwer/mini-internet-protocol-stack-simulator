# a protocol.py file containing the header definitions and classes for Layers 2, 3, and 4

class Segment:
    def __init__(self, src_port, dst_port, length, checksum, type, sequence_number, data):
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = length
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