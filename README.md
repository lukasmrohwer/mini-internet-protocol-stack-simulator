# Mini Internet Protocol Stack Simulator

This is a simplified network simulator designed to demonstrate data is delivered between hosts through layer 2, 3 and 4 of the OSI model.

## Implementation Details

TO-DO

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
