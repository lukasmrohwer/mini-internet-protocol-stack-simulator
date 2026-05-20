# a devices.py file implementing the Host and Router classes
from protocol import Segment, Packet, Frame

class Host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.sequence_number = 0
        self.expected_seq_num = 0
        self.waiting_for_ack = False

    def application_send(self, data, src_port, dst_port):
        self.transport_send(data, src_port, dst_port)

    def transport_send(self, data, src_port, dst_port):
        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(data)}")
        
        segment = Segment(src_port, dst_port, 0, self.sequence_number, data)
        print(f"{self.name}: Layer 4: Checksum computed")
        print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={self.sequence_number}) (encapsulation)")

        self.waiting_for_ack = True
        while self.waiting_for_ack:
            self.network_send(segment)
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
        self.sequence_number = 1 - self.sequence_number

    def transport_receive(self, segment):
        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        if not segment.verify_checksum():
                    print(f"{self.name}: Layer 4: Segment discarded due to checksum error")
                    return
        print(f"{self.name}: Layer 4: Checksum verified")

        if segment.type == 0:
            if segment.sequence_number == self.expected_seq_num:
                print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
                self.expected_seq_num = 1 - self.expected_seq_num

            ack_segment = Segment(None, None, 1, segment.sequence_number, "")
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={ack_segment.sequence_number})")

            self.network_send(ack_segment)
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        elif segment.type == 1:
            print(f"{self.name}: Layer 4: ACK received: seq={segment.sequence_number}")
            if segment.sequence_number == self.sequence_number:
                self.waiting_for_ack = False
            else:
                print(f"{self.name}: Layer 4: Segment retransmitted due to incorrect ACK")


    def network_send(self, data, dst_ip, dst_port):
        pass

    def network_receive(self, segment):
        pass

    def link_send(self, data, dst_ip, dst_port):
        pass

class Router:
    def __init__(self, name):
        self.name = name