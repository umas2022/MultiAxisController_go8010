"""
Advanced example for controlling GO-M8010-6 motor on Windows
This example demonstrates various control modes and safety checks
"""
import time
import math
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import using relative paths from src directory
from motor_control import GO_M8010_6_Motor, scan_motor_ids


def safety_check(state):
    """Check if motor state is within safe limits"""
    if state is None:
        return False
    
    # Check temperature (should be under 80°C to avoid thermal protection)
    if state.temp > 75:
        print(f"WARNING: High temperature detected: {state.temp}°C")
        return False
    
    # Check for motor errors
    if state.merror != 0:
        print(f"ERROR: Motor error detected: {state.merror}")
        return False
    
    return True


def main():
    print("Advanced Unitree GO-M8010-6 Motor Control Example for Windows")
    print("=" * 60)
    
    # Scan for connected motors
    print("Scanning for connected motors...")
    detected_motors = scan_motor_ids(port_name="COM11", baudrate=4000000)
    
    if not detected_motors:
        print("No motors detected on COM11. Please check connection.")
        return
    
    print(f"Detected motors: {detected_motors}")
    
    # Connect to motor with ID 0
    motor_id = 0
    if motor_id not in detected_motors:
        print(f"Motor with ID {motor_id} not detected. Exiting.")
        return
    
    print(f"\nConnecting to motor ID {motor_id} on COM11...")
    
    try:
        # Create motor controller instance
        motor = GO_M8010_6_Motor(port_name="COM11", motor_id=motor_id, baudrate=4000000)
        
        print("Enabling motor...")
        response = motor.enable_motor()
        if response:
            print(f"Motor enabled. Initial state:")
            print(f"  Position: {response.q:.3f} rad")
            print(f"  Velocity: {response.dq:.3f} rad/s")
            print(f"  Torque: {response.tau:.3f} N.m")
            print(f"  Temperature: {response.temp}°C")
            print(f"  Error code: {response.merror}")
        else:
            print("Failed to enable motor")
            return
        
        time.sleep(0.5)
        
        print("\nStarting advanced control demonstration...")
        print("1. Sinusoidal position control")
        print("2. Velocity control")
        print("3. Torque control")
        print("Press Ctrl+C to stop")
        
        start_time = time.time()
        try:
            while True:
                current_time = time.time() - start_time
                
                # Safety check
                state = motor.get_motor_state()
                if not safety_check(state):
                    print("Safety check failed, disabling motor")
                    motor.disable_motor()
                    break
                
                # Phase 1: Sinusoidal position control (first 10 seconds)
                if current_time < 10.0:
                    # Generate sinusoidal position reference
                    amplitude = 0.5  # 0.5 rad amplitude
                    frequency = 0.5  # 0.5 Hz
                    target_pos = amplitude * math.sin(2 * math.pi * frequency * current_time)
                    
                    # Use PD control to track the position
                    response = motor.set_position(target_pos, kp=15.0, kd=0.8, tau=0.0)
                    
                    if current_time == 0 or int(current_time) != int(current_time - 0.002):
                        print(f"\nPhase 1 - Sine wave pos control | t={current_time:.1f}s | Pos_ref: {target_pos:.3f}")
                
                # Phase 2: Velocity control (10-20 seconds)
                elif current_time < 20.0:
                    # Constant velocity
                    target_vel = 1.0  # 1.0 rad/s
                    
                    response = motor.set_velocity(target_vel, kd=0.8, tau=0.0)
                    
                    if int(current_time) != int(current_time - 0.002):
                        print(f"Phase 2 - Velocity control | t={current_time:.1f}s | Vel_ref: {target_vel:.3f}")
                
                # Phase 3: Torque control (20-30 seconds)
                elif current_time < 30.0:
                    # Sinusoidal torque
                    amplitude = 0.5  # 0.5 N.m amplitude
                    frequency = 0.2  # 0.2 Hz
                    target_tau = amplitude * math.sin(2 * math.pi * frequency * (current_time - 20))
                    
                    response = motor.set_torque(target_tau)
                    
                    if int(current_time) != int(current_time - 0.002):
                        print(f"Phase 3 - Torque control | t={current_time:.1f}s | Tau_ref: {target_tau:.3f}")
                
                # After 30 seconds, repeat from phase 1
                else:
                    start_time = time.time()  # Reset timer to restart cycle
                
                # Print current state periodically
                if state and int((current_time * 100) % 10) == 0:  # Every second
                    print(f"  Current - Pos: {state.q:.3f}, Vel: {state.dq:.3f}, Tau: {state.tau:.3f}, Temp: {state.temp}°C")
                
                time.sleep(0.002)  # 2ms delay (500 Hz)
        
        except KeyboardInterrupt:
            print("\n\nStopping motor...")
            
            # Stop motor safely
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