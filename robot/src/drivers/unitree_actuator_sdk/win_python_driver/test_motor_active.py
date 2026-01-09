"""
Test active motor communication with GO-M8010-6 motor
Trying different command patterns based on original examples
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.serial_port import SerialPort
from src.motor_control import MotorCmd, MotorType, MotorMode
from src.motor_protocol import query_motor_mode, query_gear_ratio, MotorData

def test_active_motor_command():
    print("Testing Active Motor Communication")
    print("="*50)
    
    # Try to open serial port
    try:
        serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=0.1)
        print("✓ Serial port opened successfully")
    except Exception as e:
        print(f"✗ Failed to open serial port: {e}")
        return
    
    # Test 1: Use the exact pattern from original example
    print("\nTest 1: Using original example pattern (non-zero velocity)")
    cmd = MotorCmd()
    cmd.motorType = MotorType.GO_M8010_6
    cmd.id = 0
    cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd.kp = 0.0
    cmd.kd = 0.01
    cmd.q = 0.0
    # Use non-zero velocity like in original example
    cmd.dq = 6.28 * query_gear_ratio(MotorType.GO_M8010_6)
    cmd.tau = 0.0
    
    print(f"Command: id={cmd.id}, mode={cmd.mode}, kp={cmd.kp}, kd={cmd.kd}, q={cmd.q}, dq={cmd.dq:.2f}, tau={cmd.tau}")
    
    # Process and send
    packed_data = cmd.modify_data()
    print(f"✓ Command processed, data length: {len(packed_data)}, data: {packed_data.hex()}")
    
    try:
        serial_port.serial_port.reset_input_buffer()
        success = serial_port.send(packed_data)
        if success:
            print("✓ Command sent successfully")
        else:
            print("✗ Failed to send command")
        
        # Wait for response (use same timing as original)
        time.sleep(0.0002)  # Original code uses 200 microseconds
        
        response = serial_port.recv(size=16)
        if response:
            print(f"✓ Received response: {response.hex()}")
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
    
    except Exception as e:
        print(f"✗ Error during communication: {e}")
    
    # Test 2: Try with negative velocity
    print(f"\nTest 2: Using negative velocity (-6.28*gear_ratio)")
    cmd2 = MotorCmd()
    cmd2.motorType = MotorType.GO_M8010_6
    cmd2.id = 0
    cmd2.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd2.kp = 0.0
    cmd2.kd = 0.01
    cmd2.q = 0.0
    # Use negative velocity
    cmd2.dq = -6.28 * query_gear_ratio(MotorType.GO_M8010_6)
    cmd2.tau = 0.0
    
    print(f"Command: id={cmd2.id}, mode={cmd2.mode}, kp={cmd2.kp}, kd={cmd2.kd}, q={cmd2.q}, dq={cmd2.dq:.2f}, tau={cmd2.tau}")
    
    # Process and send
    packed_data2 = cmd2.modify_data()
    print(f"✓ Command processed, data length: {len(packed_data2)}, data: {packed_data2.hex()}")
    
    try:
        serial_port.serial_port.reset_input_buffer()
        success = serial_port.send(packed_data2)
        if success:
            print("✓ Command sent successfully")
        else:
            print("✗ Failed to send command")
        
        # Wait for response
        time.sleep(0.0002)  # 200 microseconds
        
        response = serial_port.recv(size=16)
        if response:
            print(f"✓ Received response: {response.hex()}")
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
    
    except Exception as e:
        print(f"✗ Error during communication: {e}")
    
    # Test 3: Try simple zero command again (like in scan)
    print(f"\nTest 3: Simple zero command (like in motor scan)")
    cmd3 = MotorCmd()
    cmd3.motorType = MotorType.GO_M8010_6
    cmd3.id = 0
    cmd3.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd3.kp = 0.0
    cmd3.kd = 0.01
    cmd3.q = 0.0
    cmd3.dq = 0.0
    cmd3.tau = 0.0
    
    print(f"Command: id={cmd3.id}, mode={cmd3.mode}, kp={cmd3.kp}, kd={cmd3.kd}, q={cmd3.q}, dq={cmd3.dq}, tau={cmd3.tau}")
    
    # Process and send
    packed_data3 = cmd3.modify_data()
    print(f"✓ Command processed, data length: {len(packed_data3)}, data: {packed_data3.hex()}")
    
    try:
        serial_port.serial_port.reset_input_buffer()
        success = serial_port.send(packed_data3)
        if success:
            print("✓ Command sent successfully")
        else:
            print("✗ Failed to send command")
        
        # Wait for response with longer delay to ensure motor responds
        time.sleep(0.005)  # 5ms wait
        
        response = serial_port.recv(size=16)
        if response:
            print(f"✓ Received response: {response.hex()}")
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
    
    except Exception as e:
        print(f"✗ Error during communication: {e}")
    
    finally:
        serial_port.close()

if __name__ == "__main__":
    test_active_motor_command()