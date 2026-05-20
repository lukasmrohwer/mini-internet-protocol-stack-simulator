# Mini Internet Protocol Stack Simulator

This is a simplified network simulator designed to demonstrate data is delivered between hosts through layer 2, 3 and 4 of the OSI model.

## Implementation Explanation

### Project Structure

- **`devices.py`**: Implements the `Host` and `Router` classes containing the core logic for the different networking layers.
- **`protocol.py`**: Defines the header definitions and classes used for encapsulation: `Segment` (Layer 4), `Packet` (Layer 3), and `Frame` (Layer 2).
- **`config.py`**: Stores the fixed parameters for  IP addresses, MAC addresses, ARP tables, and routing tables for all devices.
- **`main.py`**: The main entry point of the simulation. It initializes the network devices (Host A, Host B, and Router R1), connects them, and initiates the data transmission.

### Layer Breakdown

Transport Layer
The transport layer receives the data from the application and is segmented into UDP-like segments of length up to 500 bytes. The segment includes port numbers to identify sending and receiving applications, the data itself along with the length of the segment and its type, and the checksum of the segment along with a sequence number used for error detection.

data segmentation, error detection, data transfer


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
