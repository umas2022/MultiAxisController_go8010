"""
GO-M8010-6 Motor Protocol Implementation
Based on the Unitree motor communication protocol
"""
import struct
from enum import Enum
from typing import Union
import sys
import os

# Add the utils directory to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

from crc import crc_ccitt


class MotorType(Enum):
    """Motor type enumeration"""
    A1 = 0
    B1 = 1
    GO_M8010_6 = 2


class MotorMode(Enum):
    """Motor mode enumeration"""
    BRAKE = 0
    FOC = 1
    CALIBRATE = 2


class MotorStatus(Enum):
    """Motor status values"""
    LOCKED = 0
    FOC_CLOSED_LOOP = 1
    ENCODER_CALIBRATION = 2
    RESERVED = 3


def query_motor_mode(motor_type: MotorType, mode: MotorMode) -> int:
    """
    Query the appropriate mode value for the motor type and mode
    
    Args:
        motor_type: Type of motor
        mode: Desired motor mode
    
    Returns:
        Mode value as integer
    """
    # For GO-M8010-6, the mode value corresponds to the status field in RIS_Mode_t
    if motor_type == MotorType.GO_M8010_6:
        if mode == MotorMode.BRAKE:
            return MotorStatus.LOCKED.value
        elif mode == MotorMode.FOC:
            return MotorStatus.FOC_CLOSED_LOOP.value
        elif mode == MotorMode.CALIBRATE:
            return MotorStatus.ENCODER_CALIBRATION.value
    return 0


def query_gear_ratio(motor_type: MotorType) -> float:
    """
    Query the gear ratio for the specified motor type
    
    Args:
        motor_type: Type of motor
    
    Returns:
        Gear ratio as float
    """
    # Known gear ratios for Unitree motors
    gear_ratios = {
        MotorType.A1: 9.73,
        MotorType.B1: 6.0,
        MotorType.GO_M8010_6: 6.0  # GO-M8010-6 typically has 6.0 gear ratio
    }
    return gear_ratios.get(motor_type, 1.0)


class RISMode:
    """RIS Mode structure for GO-M8010-6 motor"""
    
    def __init__(self, motor_id: int = 0, status: int = 1, reserved: int = 0):
        self.id = motor_id & 0xF  # 4 bits for ID (0-15)
        self.status = status & 0x7  # 3 bits for status
        self.reserved = reserved & 0x1  # 1 bit reserved
    
    def pack(self) -> bytes:
        """Pack the mode data into bytes"""
        # Pack as: (id | (status << 4) | (reserved << 7))
        mode_byte = (self.id & 0x0F) | ((self.status & 0x07) << 4) | ((self.reserved & 0x01) << 7)
        return struct.pack('<B', mode_byte)
    
    @classmethod
    def unpack(cls, data: bytes):
        """Unpack mode data from bytes"""
        if len(data) < 1:
            raise ValueError("Insufficient data for RISMode unpacking")
        
        mode_byte = struct.unpack('<B', data[0:1])[0]
        id_val = mode_byte & 0x0F
        status_val = (mode_byte >> 4) & 0x07
        reserved_val = (mode_byte >> 7) & 0x01
        
        return cls(id_val, status_val, reserved_val)


class RISComd:
    """RIS Command structure for GO-M8010-6 motor"""
    
    def __init__(self, tor_des: float = 0.0, spd_des: float = 0.0, pos_des: float = 0.0, 
                 k_pos: float = 0.0, k_spd: float = 0.0):
        # Convert floating point values to fixed-point integers
        # tor_des: q8 format (multiply by 2^8)
        self.tor_des = int(tor_des * (2**8))
        # spd_des: q7 format (multiply by 2^7) 
        self.spd_des = int(spd_des * (2**7))
        # pos_des: q15 format (multiply by 2^15)
        self.pos_des = int(pos_des * (2**15))
        # k_pos: q15 format (multiply by 2^15, range 0.0-1.0)
        self.k_pos = max(0, min(32767, int(k_pos * (2**15))))
        # k_spd: q15 format (multiply by 2^15, range 0.0-1.0)
        self.k_spd = max(0, min(32767, int(k_spd * (2**15))))
    
    def pack(self) -> bytes:
        """Pack the command data into bytes"""
        # Pack as little-endian: tor_des(int16), spd_des(int16), pos_des(int32), k_pos(uint16), k_spd(uint16)
        # Total size should be 2+2+4+2+2=12 bytes as per protocol
        # Correct format string: signed short, signed short, signed int, unsigned short, unsigned short
        return struct.pack('<hhiHH',
                          self.tor_des, self.spd_des, self.pos_des,
                          self.k_pos, self.k_spd)
    
    @classmethod
    def unpack(cls, data: bytes):
        """Unpack command data from bytes (for debugging)"""
        if len(data) < 12:
            raise ValueError("Insufficient data for RISComd unpacking")
        
        tor_des, spd_des, pos_des, k_pos, k_spd = struct.unpack('<hhiHH', data[:12])
        
        # Convert back to floating point values
        tor_des_float = tor_des / (2**8)
        spd_des_float = spd_des / (2**7)
        pos_des_float = pos_des / (2**15)
        k_pos_float = k_pos / (2**15)
        k_spd_float = k_spd / (2**15)
        
        return cls(tor_des_float, spd_des_float, pos_des_float, k_pos_float, k_spd_float)


class RISFbk:
    """RIS Feedback structure for GO-M8010-6 motor"""
    
    def __init__(self, torque: float = 0.0, speed: float = 0.0, pos: float = 0.0, 
                 temp: int = 0, merror: int = 0, force: int = 0, reserved: int = 0):
        # Store raw values
        self.torque_raw = int(torque * (2**8))  # q8 format
        self.speed_raw = int(speed * (2**7))    # q7 format
        self.pos_raw = int(pos * (2**15))       # q15 format
        self.temp = temp                        # int8
        self.merror = merror & 0x7              # 3 bits
        self.force = force & 0xFFF              # 12 bits
        self.reserved = reserved & 0x1          # 1 bit
    
    def pack(self) -> bytes:
        """Pack the feedback data into bytes"""
        # Pack as little-endian: torque(int16), speed(int16), pos(int32), temp(int8),
        # combined byte for MError(3bits), force(12bits), reserved(1bit)
        combined = (self.merror & 0x7) | ((self.force & 0xFFF) << 3) | ((self.reserved & 0x1) << 15)
        return struct.pack('<hhhiBH',
                          self.torque_raw, self.speed_raw, self.pos_raw,
                          combined, self.temp)
    
    @classmethod
    def unpack(cls, data: bytes):
        """Unpack feedback data from bytes"""
        if len(data) < 11:
            raise ValueError("Insufficient data for RISFbk unpacking")
        
        torque_raw, speed_raw, pos_raw, combined, temp = struct.unpack('<hhhiBH', data[:11])
        
        # Extract individual fields from combined value
        merror = combined & 0x7
        force = (combined >> 3) & 0xFFF
        reserved = (combined >> 15) & 0x1
        
        # Convert back to floating point values
        torque = torque_raw / (2**8)
        speed = speed_raw / (2**7)
        pos = pos_raw / (2**15)
        
        return cls(torque, speed, pos, temp, merror, force, reserved)
    
    @property
    def torque(self) -> float:
        """Torque in N.m"""
        return self.torque_raw / (2**8)
    
    @property
    def speed(self) -> float:
        """Speed in rad/s"""
        return self.speed_raw / (2**7)
    
    @property
    def position(self) -> float:
        """Position in radians"""
        return self.pos_raw / (2**15)


class ControlData:
    """Control data packet for GO-M8010-6 motor"""
    
    def __init__(self, mode: RISMode = None, comd: RISComd = None):
        self.head = b'\xFF\xFE'  # Fixed header for GO-M8010-6
        self.mode = mode or RISMode()
        self.comd = comd or RISComd()
        self.crc16 = 0
    
    def pack(self, calculate_crc: bool = True) -> bytes:
        """Pack the control data into bytes"""
        mode_bytes = self.mode.pack()
        comd_bytes = self.comd.pack()
        
        # Combine header, mode, and command (without CRC yet)
        data_without_crc = self.head + mode_bytes + comd_bytes
        
        if calculate_crc:
            # Calculate CRC for the data without CRC field
            self.crc16 = crc_ccitt(data_without_crc)
        
        # Pack final data with CRC
        crc_bytes = struct.pack('<H', self.crc16)
        return data_without_crc + crc_bytes
    
    @classmethod
    def create_from_params(cls, motor_id: int, mode_status: int, torque: float, 
                          speed: float, position: float, kp: float, kd: float):
        """Create a ControlData packet with specified parameters"""
        mode = RISMode(motor_id, mode_status)
        comd = RISComd(torque, speed, position, kp, kd)
        return cls(mode, comd)


class MotorData:
    """Motor feedback data packet for GO-M8010-6 motor"""
    
    def __init__(self, head: bytes = None, mode: RISMode = None, fbk: RISFbk = None, crc16: int = 0):
        self.head = head or b'\xFF\xFE'
        self.mode = mode or RISMode()
        self.fbk = fbk or RISFbk()
        self.crc16 = crc16
    
    def validate_crc(self, received_data: bytes) -> bool:
        """Validate CRC of received data"""
        if len(received_data) < 16:
            return False
        
        # Calculate CRC for all bytes except the last 2 (CRC itself)
        calculated_crc = crc_ccitt(received_data[:-2])
        received_crc = struct.unpack('<H', received_data[-2:])[0]
        
        return calculated_crc == received_crc
    
    @classmethod
    def unpack(cls, data: bytes):
        """Unpack motor feedback data from bytes"""
        if len(data) < 16:
            raise ValueError(f"Insufficient data for MotorData unpacking, got {len(data)} bytes")
        
        # Validate CRC first
        crc_validator = cls()
        if not crc_validator.validate_crc(data):
            print(f"CRC validation failed for received data: {data.hex()}")
            # Continue anyway but warn
            pass
        
        head = data[0:2]
        mode = RISMode.unpack(data[2:3])
        fbk = RISFbk.unpack(data[3:14])
        crc16 = struct.unpack('<H', data[14:16])[0]
        
        return cls(head, mode, fbk, crc16)
    
    @property
    def motor_id(self) -> int:
        """Motor ID from the mode field"""
        return self.mode.id
    
    @property
    def status(self) -> int:
        """Status from the mode field"""
        return self.mode.status