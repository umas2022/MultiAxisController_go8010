"""
Debug serial communication with GO-M8010-6 motor
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.serial_port import SerialPort
from src.motor_control import MotorCmd, MotorType, MotorMode
from src.motor_protocol import query_motor_mode, RISMode, RISComd, ControlData, MotorData

def debug_motor_connection():
    print("Debugging GO-M8010-6 Motor Connection")
    print("="*50)
    
    # Try to open serial port
    try:
        serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=0.1)
        print("✓ Serial port opened successfully")
    except Exception as e:
        print(f"✗ Failed to open serial port: {e}")
        return
    
    # Create a command manually
    cmd = MotorCmd()
    cmd.motorType = MotorType.GO_M8010_6
    cmd.id = 0  # Target motor ID 0
    cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd.kp = 0.0
    cmd.kd = 0.01
    cmd.q = 0.0
    cmd.dq = 0.0
    cmd.tau = 0.0
    
    print(f"Created command for motor ID {cmd.id}")
    
    # Process the command like original C++ code
    packed_data = cmd.modify_data()
    print(f"✓ Command processed, data length: {len(packed_data)}, data: {packed_data.hex()}")
    
    # Test sending raw data
    print("\nTesting raw data transmission...")
    try:
        # Clear input buffer first
        serial_port.serial_port.reset_input_buffer()
        print("✓ Input buffer cleared")
        
        # Send the command
        success = serial_port.send(packed_data)
        if success:
            print("✓ Command sent successfully")
        else:
            print("✗ Failed to send command")
            return
        
        # Wait a bit for response (original code uses 200us delay)
        time.sleep(0.002)  # 2ms, slightly longer than original 200us
        
        # Try to receive response
        response = serial_port.recv(size=16)
        if response:
            print(f"✓ Received response: {response.hex()}")
            print(f"  Response length: {len(response)} bytes")
            
            # Try to parse response
            try:
                motor_data = MotorData.unpack(response)
                print(f"  Motor ID: {motor_data.motor_id}")
                print(f"  Position: {motor_data.fbk.position:.3f}")
                print(f"  Speed: {motor_data.fbk.speed:.3f}")
                print(f"  Torque: {motor_data.fbk.torque:.3f}")
                print(f"  Temperature: {motor_data.fbk.temp}°C")
                print(f"  Error: {motor_data.fbk.merror}")
            except Exception as e:
                print(f"  ✗ Failed to parse response: {e}")
        else:
            print("✗ No response received")
            print("  This could be due to:")
            print("  - Motor not powered on")
            print("  - Wrong COM port")
            print("  - Incorrect motor ID")
            print("  - Motor in wrong mode")
            print("  - Communication timing issue")
    
    except Exception as e:
        print(f"✗ Error during communication: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        serial_port.close()

if __name__ == "__main__":
    debug_motor_connection()