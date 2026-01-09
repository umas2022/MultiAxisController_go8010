"""
Comprehensive test for motor communication with various parameters
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.serial_port import SerialPort
from src.motor_control import MotorCmd, MotorType, MotorMode
from src.motor_protocol import query_motor_mode, query_gear_ratio, MotorData

def test_different_parameters():
    print("Comprehensive Motor Communication Test")
    print("="*50)
    
    # Test different timeout and delay values
    timeout_values = [0.02, 0.05, 0.1, 0.2]
    delay_values = [0.0002, 0.001, 0.002, 0.005, 0.01]
    
    for timeout in timeout_values:
        print(f"\n--- Testing with timeout={timeout}s ---")
        try:
            serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=timeout)
            
            for delay in delay_values:
                print(f"  Testing with delay={delay}s...")
                
                # Create command
                cmd = MotorCmd()
                cmd.motorType = MotorType.GO_M8010_6
                cmd.id = 0
                cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
                cmd.kp = 0.0
                cmd.kd = 0.01
                cmd.q = 0.0
                cmd.dq = 0.0  # Zero velocity command
                cmd.tau = 0.0
                
                # Process and send
                packed_data = cmd.modify_data()
                
                # Use direct send_recv with specific delay
                response = serial_port.send_recv(packed_data, recv_size=16, delay=delay)
                
                if response:
                    print(f"    ✓ Response received with delay={delay}s: {response.hex()}")
                    try:
                        motor_data = MotorData.unpack(response)
                        print(f"      Motor ID: {motor_data.motor_id}, Pos: {motor_data.fbk.position:.3f}, Temp: {motor_data.fbk.temp}°C")
                    except Exception as e:
                        print(f"      Could not parse: {e}")
                    # If we get a response, we can break early
                    serial_port.close()
                    return
                else:
                    print(f"    ✗ No response with delay={delay}s")
            
            serial_port.close()
            
        except Exception as e:
            print(f"  ✗ Error with timeout={timeout}: {e}")
    
    print("\n--- Trying alternative approach: Send multiple commands rapidly ---")
    try:
        serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=0.1)
        
        # Send several commands in a row
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = 0
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = 0.01
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.tau = 0.0
        
        packed_data = cmd.modify_data()
        
        for i in range(5):
            print(f"  Sending command #{i+1}...")
            response = serial_port.send_recv(packed_data, recv_size=16, delay=0.002)
            if response:
                print(f"    ✓ Response #{i+1}: {response.hex()}")
                try:
                    motor_data = MotorData.unpack(response)
                    print(f"      Motor ID: {motor_data.motor_id}, Pos: {motor_data.fbk.position:.3f}")
                except Exception as e:
                    print(f"      Could not parse: {e}")
            else:
                print(f"    ✗ No response #{i+1}")
            time.sleep(0.01)  # Small pause between commands
        
        serial_port.close()
        
    except Exception as e:
        print(f"  ✗ Error in rapid command test: {e}")

def test_with_original_pattern():
    print("\n--- Testing with original example pattern ---")
    try:
        serial_port = SerialPort(port_name="COM11", baudrate=4000000, timeout=0.1)
        
        # Use the exact pattern from the original C++ example
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = 0
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = 0.01
        cmd.q = 0.0
        cmd.dq = -6.28 * query_gear_ratio(MotorType.GO_M8010_6)  # Negative velocity from original
        cmd.tau = 0.0
        
        print(f"Command: id={cmd.id}, mode={cmd.mode}, kp={cmd.kp}, kd={cmd.kd}, q={cmd.q}, dq={cmd.dq:.2f}, tau={cmd.tau}")
        
        packed_data = cmd.modify_data()
        print(f"Data: {packed_data.hex()}")
        
        # Send multiple times as in a continuous loop
        responses = []
        for i in range(10):  # Send 10 commands like in the original loop
            response = serial_port.send_recv(packed_data, recv_size=16, delay=0.0002)
            if response:
                responses.append(response)
                print(f"  Response {i+1}: {response.hex()}")
                try:
                    motor_data = MotorData.unpack(response)
                    print(f"    ID: {motor_data.motor_id}, Pos: {motor_data.fbk.position:.3f}, Vel: {motor_data.fbk.speed:.3f}")
                except Exception as e:
                    print(f"    Parse error: {e}")
            else:
                print(f"  No response {i+1}")
            time.sleep(0.0002)  # Match original usleep(200) = 200 microseconds
        
        print(f"Total responses received: {len(responses)}")
        serial_port.close()
        
    except Exception as e:
        print(f"  ✗ Error in original pattern test: {e}")

if __name__ == "__main__":
    test_different_parameters()
    test_with_original_pattern()
    print("\nTest completed.")