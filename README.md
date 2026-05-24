# Mini Internet Protocol Stack Simulator

Lukas Rohwer (24215157), Harrison Chambers (24328083)

This is a simplified network simulator designed to demonstrate data is delivered between hosts through layer 2, 3 and 4 of the OSI model.

## Implementation Explanation

`main.py` is the main entry file, which is invoked from the command line along with an argument: an integer representing the size of the message in bytes. This file initiates the host and router objects representing devices in the network and begins the delivery of data from host A to host B.

`config.py` defines fixed parameters used in the simulation, including the IP addresses and MAC addresses of the devices, the routing tables used by the network layer, and ARP tables used by the link layer.

`devices.py` defines the Host and Router classes, including information about each, including their IP address, MAC address, router tables, their respective layer objects, as well as functions for receiving information from the application layer or the network. These are the classes defining the objects created in main.py. 

`protocol.py` contains the class definitions for the protocol headers Segment, Packet, and Frame, as well as the classes for Layers 2, 3, and 4 of the OSI model. Each layer class defines a function for sending and receiving data, passing it up or down the stack to the next layer.

## Usage

To run the simulator, you need to execute `main.py` and provide the application message size as a command-line argument. The message size is the length of the message in bytes that Host A will send to Host B (e.g. 100 for a 100-byte message).

### Prerequisites
- Python 3.x

### Running the Simulation

Run the simulation using the following command format:

```bash
python main.py <message_size>
```

**Example:**
```bash
python main.py 10
```

This will execute the simulation and output a detailed trace of the operations of each OSI layer across the sending host A, the router, and the receiving host B.
