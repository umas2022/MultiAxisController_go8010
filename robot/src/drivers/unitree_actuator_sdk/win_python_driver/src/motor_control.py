"""
GO-M8010-6 Motor Control Class
Provides high-level interface for controlling Unitree GO-M8010-6 motors
"""
from typing import Optional
import time
import sys
import os

# Dynamically add the src directory to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import using absolute module names (now that src is in path)
import serial_port
import motor_protocol
from motor_protocol import (
    MotorType, MotorMode, MotorData, ControlData,
    RISMode, RISComd, RISFbk, query_motor_mode, query_gear_ratio
)

# Create aliases for external access
SerialPort = serial_port.SerialPort


class MotorCmd:
    """Motor command structure"""
    
    def __init__(self):
        self.motorType = MotorType.GO_M8010_6
        self.hex_len = 0
        self.id = 0
        self.mode = 1  # Default to FOC mode
        self.tau = 0.0
        self.dq = 0.0
        self.q = 0.0
        self.kp = 0.0
        self.kd = 0.0
        # Internal storage for processed data
        self._processed_data = None
    
    def modify_data(self):
        """Process the motor command data to prepare for sending"""
        # Create control packet with current parameters
        mode_obj = RISMode(motor_id=self.id, status=self.mode)
        comd_obj = RISComd(tor_des=self.tau, spd_des=self.dq, pos_des=self.q, k_pos=self.kp, k_spd=self.kd)
        control_data = ControlData(mode=mode_obj, comd=comd_obj)
        
        # Pack the data and store internally
        packed_data = control_data.pack()
        self._processed_data = packed_data
        self.hex_len = len(packed_data)
        return packed_data
    
    def get_motor_send_data(self):
        """Get the processed motor command data for sending"""
        if self._processed_data is None:
            self.modify_data()
        return self._processed_data


class MotorDataResult:
    """Motor data result structure"""
    
    def __init__(self):
        self.motorType = MotorType.GO_M8010_6
        self.hex_len = 0
        self.motor_id = 0
        self.mode = 0
        self.temp = 0
        self.merror = 0
        self.tau = 0.0
        self.dq = 0.0
        self.q = 0.0


class GO_M8010_6_Motor:
    """GO-M8010-6 Motor Controller"""
    
    def __init__(self, port_name: str = "COM11", motor_id: int = 0, baudrate: int = 4000000):
        """
        Initialize the GO-M8010-6 motor controller
        
        Args:
            port_name: Serial port name (e.g., "COM11")
            motor_id: Motor ID (0-15)
            baudrate: Baud rate for communication
        """
        self.port_name = port_name
        self.motor_id = motor_id
        self.baudrate = baudrate
        self.serial_port = SerialPort(port_name, baudrate)
        self.gear_ratio = query_gear_ratio(MotorType.GO_M8010_6)
    
    def send_command(self, cmd: MotorCmd) -> Optional[MotorDataResult]:
        """
        Send a command to the motor and receive response
        
        Args:
            cmd: Motor command to send
            
        Returns:
            Motor data response or None if error
        """
        # Process the command data like in the original C++ code
        # This mimics the modify_data() and get_motor_send_data() pattern from C++
        cmd.modify_data()  # Process data like MotorCmd::modify_data()
        packed_data = cmd.get_motor_send_data()  # Get processed data like MotorCmd::get_motor_send_data()
        
        # Send the command and receive response
        response = self.serial_port.send_recv(packed_data, recv_size=16)
        
        if response is None or len(response) == 0:
            print(f"No response received from motor ID {cmd.id}")
            return None
        
        try:
            # Parse the response
            motor_data = MotorData.unpack(response)
            
            # Create result object
            result = MotorDataResult()
            result.motorType = cmd.motorType
            result.motor_id = motor_data.motor_id
            result.mode = motor_data.status
            result.temp = motor_data.fbk.temp
            result.merror = motor_data.fbk.merror
            result.tau = motor_data.fbk.torque
            result.dq = motor_data.fbk.speed
            result.q = motor_data.fbk.position
            
            return result
        except Exception as e:
            print(f"Error parsing motor response: {e}")
            return None
    
    def enable_motor(self):
        """Enable the motor in FOC mode with minimal kp/kd"""
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = 0.01
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.tau = 0.0
        
        return self.send_command(cmd)
    
    def disable_motor(self):
        """Disable the motor (brake mode)"""
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.BRAKE)
        cmd.kp = 0.0
        cmd.kd = 0.0
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.tau = 0.0
        
        return self.send_command(cmd)
    
    def set_position(self, position: float, kp: float = 10.0, kd: float = 1.0, tau: float = 0.0):
        """
        Set motor position with PD control
        
        Args:
            position: Target position in radians
            kp: Position gain
            kd: Velocity gain
            tau: Feedforward torque
        """
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = kp
        cmd.kd = kd
        cmd.q = position
        cmd.dq = 0.0
        cmd.tau = tau
        
        return self.send_command(cmd)
    
    def set_velocity(self, velocity: float, kd: float = 1.0, tau: float = 0.0):
        """
        Set motor velocity
        
        Args:
            velocity: Target velocity in rad/s
            kd: Velocity gain
            tau: Feedforward torque
        """
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = kd
        cmd.q = 0.0
        cmd.dq = velocity
        cmd.tau = tau
        
        return self.send_command(cmd)
    
    def set_torque(self, torque: float):
        """
        Set motor torque directly
        
        Args:
            torque: Target torque in N.m
        """
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = 0.0
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.tau = torque
        
        return self.send_command(cmd)
    
    def get_motor_state(self):
        """Get current motor state without changing control parameters"""
        cmd = MotorCmd()
        cmd.motorType = MotorType.GO_M8010_6
        cmd.id = self.motor_id
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.kp = 0.0
        cmd.kd = 0.01
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.tau = 0.0
        
        return self.send_command(cmd)
    
    def close(self):
        """Close the connection"""
        self.serial_port.close()
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup


def scan_motor_ids(port_name: str = "COM11", baudrate: int = 4000000, id_range: range = range(0, 16)):
    """
    Scan for connected motors on the specified port
    
    Args:
        port_name: Serial port name
        baudrate: Communication baud rate
        id_range: Range of IDs to scan
    
    Returns:
        List of detected motor IDs
    """
    detected_motors = []
    serial_port = SerialPort(port_name, baudrate)
    
    try:
        for motor_id in id_range:
            cmd = MotorCmd()
            cmd.motorType = MotorType.GO_M8010_6
            cmd.id = motor_id
            cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
            cmd.kp = 0.0
            cmd.kd = 0.01
            cmd.q = 0.0
            cmd.dq = 0.0
            cmd.tau = 0.0
            
            # Process the command data like in the original C++ code
            cmd.modify_data()  # Process data like MotorCmd::modify_data()
            packed_data = cmd.get_motor_send_data()  # Get processed data like MotorCmd::get_motor_send_data()
            response = serial_port.send_recv(packed_data, recv_size=16)
            
            if response is not None and len(response) > 0:
                try:
                    # Try to parse the response to confirm it's a valid motor response
                    motor_data = MotorData.unpack(response)
                    if motor_data.motor_id == motor_id:
                        detected_motors.append(motor_id)
                        print(f"Motor found at ID: {motor_id}")
                        print(f"  Position: {motor_data.fbk.position:.3f}")
                        print(f"  Speed: {motor_data.fbk.speed:.3f}")
                        print(f"  Temperature: {motor_data.fbk.temp}°C")
                        print(f"  Error: {motor_data.fbk.merror}")
                except:
                    # Response might not be from a motor, continue scanning
                    continue
            
            # Small delay between scans
            time.sleep(0.05)
    
    finally:
        serial_port.close()
    
    return detected_motors