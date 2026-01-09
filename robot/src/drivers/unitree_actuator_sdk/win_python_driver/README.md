# Unitree GO-M8010-6 Windows Python Driver

This directory contains a Windows-compatible Python driver for controlling Unitree GO-M8010-6 motors. The driver implements the same protocol as the original C++ SDK but runs natively on Windows with Python.

## Features

- Pure Python implementation compatible with Windows
- Same protocol implementation as original C++ SDK
- Support for GO-M8010-6 motor control via serial communication
- Compatible with COM ports on Windows systems
- High-level motor control interface

## Requirements

- Python 3.x
- pyserial library
- Access to COM port (may require administrator privileges)

## Installation

1. Install required packages:
   ```bash
   pip install pyserial
   ```

2. Ensure you have access to the COM port your motor is connected to (e.g., COM11).

## Usage

### Basic Usage

Run the basic example to connect to a GO-M8010-6 motor connected to COM11 with ID 0:

```bash
python examples/example_go_m8010_6_basic.py
```

This example demonstrates:
- Scanning for connected motors
- Establishing communication
- Setting motor to FOC mode
- Sending position and velocity commands
- Reading motor feedback

### Advanced Usage

Run the advanced example for more complex control scenarios:

```bash
python examples/example_go_m8010_6_advanced.py
```

This example demonstrates:
- Different control modes
- Safety checks
- Torque control
- Position control with PD gains

## Module Structure

- `src/motor_control.py` - Main motor control interface
- `src/motor_protocol.py` - Protocol implementation
- `src/serial_port.py` - Serial communication layer
- `utils/crc.py` - CRC calculation utilities
- `examples/` - Usage examples

## API Reference

### GO_M8010_6_Motor

Main class for controlling GO-M8010-6 motors:

```python
from motor_control import GO_M8010_6_Motor, MotorCmd, MotorMode

# Initialize motor
motor = GO_M8010_6_Motor(port_name="COM11", motor_id=0, motor_type=MotorType.GO_M8010_6)

# Set motor to FOC mode
motor.enable_motor()

# Send control command
cmd = MotorCmd()
cmd.id = 0
cmd.mode = 1  # FOC mode
cmd.q = 0.0   # Position (radians)
cmd.dq = 0.0  # Velocity (rad/s)
cmd.tau = 0.0 # Torque (Nm)
cmd.kp = 0.0  # Position gain
cmd.kd = 0.0  # Velocity gain

motor.write(cmd)
feedback = motor.read()
```

### scan_motor_ids

Function to detect connected motors:

```python
from motor_control import scan_motor_ids

detected_motors = scan_motor_ids(port_name="COM11")
print(f"Detected motors: {detected_motors}")
```

## Troubleshooting

1. **Permission denied errors**: Run the script as administrator or ensure your user has access to the COM port.
2. **No motors detected**: Verify the motor is properly connected and powered, and the correct COM port is specified.
3. **Import errors**: Make sure you run the scripts from the win_python_driver directory.

## Protocol Implementation

The driver implements the same 17-byte control packet format as the original C++ SDK:
- Header: 0xFFFE (2 bytes)
- Length: Packet length (1 byte)
- Mode: Control mode (1 byte)
- Command: 12 bytes of command data
- CRC: CRC-CCITT checksum (2 bytes)
