"""
Simple test to verify serial port functionality
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.serial_port import SerialPort
from src.motor_control import MotorCmd, MotorType, MotorMode
from src.motor_protocol import query_motor_mode, query_gear_ratio, MotorData

def test_single_connection():
    print("Testing single serial connection...")
    
    # Create command
    cmd = MotorCmd()
    cmd.motorType = MotorType.GO_M8010_6
    cmd.id = 0
    cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd.kp = 0.0
    cmd.kd = 0.01
    cmd.q = 0.0
    cmd.dq = 0.0
    cmd.tau = 0.0
    
    print(f"Command mode: {cmd.mode}")  # Should be 1 now
    
    packed_data = cmd.modify_data()
    print(f"Data to send: {packed_data.hex()}")
    
    try:
        # Open port
        serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=0.1)
        
        # Send one command
        print("Sending command...")
        response = serial_port.send_recv(packed_data, recv_size=16, delay=0.002)
        
        if response:
            print(f"Response received: {response.hex()}")
            try:
                motor_data = MotorData.unpack(response)
                print(f"Motor ID: {motor_data.motor_id}")
                print(f"Position: {motor_data.fbk.position:.3f}")
                print(f"Temperature: {motor_data.fbk.temp}°C")
            except Exception as e:
                print(f"Could not parse response: {e}")
        else:
            print("No response received")
        
        # Close port explicitly
        serial_port.close()
        print("Port closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_connection()