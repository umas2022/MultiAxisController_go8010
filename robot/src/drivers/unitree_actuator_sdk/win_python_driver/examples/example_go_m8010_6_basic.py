"""
Basic example for controlling GO-M8010-6 motor on Windows
This example connects to the motor at COM11 with ID 0 and demonstrates basic control
"""
import time
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import using relative paths from src directory
from motor_control import GO_M8010_6_Motor, MotorCmd, MotorMode, MotorType, scan_motor_ids
from motor_protocol import query_gear_ratio


def main():
    print("Unitree GO-M8010-6 Motor Control Example for Windows")
    print("=" * 50)
    
    # First, scan for connected motors
    print("Scanning for connected motors...")
    detected_motors = scan_motor_ids(port_name="COM11", baudrate=4000000)
    
    if not detected_motors:
        print("No motors detected on COM11. Please check connection.")
        return
    
    print(f"Detected motors: {detected_motors}")
    
    # Connect to motor with ID 0 (as specified in the requirements)
    motor_id = 0
    if motor_id not in detected_motors:
        print(f"Motor with ID {motor_id} not detected. Exiting.")
        return
    
    print(f"\nConnecting to motor ID {motor_id} on COM11...")
    
    try:
        # Create motor controller instance
        motor = GO_M8010_6_Motor(port_name="COM11", motor_id=motor_id, baudrate=4000000)
        
        # Enable the motor
        print("Enabling motor...")
        response = motor.enable_motor()
        if response:
            print(f"Motor enabled. Initial state - Position: {response.q:.3f}, Velocity: {response.dq:.3f}, Temp: {response.temp}°C")
        else:
            print("Failed to enable motor")
            return
        
        # Wait a moment
        time.sleep(0.5)
        
        print("\nStarting motor control demonstration...")
        print("Press Ctrl+C to stop")
        
        # Main control loop
        counter = 0
        try:
            while True:
                # Get current state
                state = motor.get_motor_state()
                if state:
                    print(f"\rPosition: {state.q:.3f} rad, Velocity: {state.dq:.3f} rad/s, Torque: {state.tau:.3f} N.m, Temp: {state.temp}°C, Error: {state.merror}", end="")
                
                # Send a small oscillating velocity command every 100 iterations
                if counter % 100 == 0:
                    # Send position command for a small oscillation
                    angle = 0.5 * 3.14159 * 0.1  # 0.1 radians (small movement)
                    response = motor.set_position(angle, kp=20.0, kd=1.0, tau=0.0)
                
                if counter % 200 == 0:
                    # Send opposite position command
                    angle = -0.5 * 3.14159 * 0.1  # -0.1 radians
                    response = motor.set_position(angle, kp=20.0, kd=1.0, tau=0.0)
                
                counter += 1
                time.sleep(0.002)  # 2ms delay (500 Hz)
                
        except KeyboardInterrupt:
            print("\n\nStopping motor...")
            
            # Set zero torque to stop safely
            motor.set_torque(0.0)
            time.sleep(0.1)
            
            # Disable the motor
            motor.disable_motor()
            print("Motor disabled. Exiting.")
    
    except Exception as e:
        print(f"Error during motor control: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()