"""
电机数据结构和数据包处理
"""

import struct
from typing import Optional
from .crc import crc_ccitt
from .utils import MotorType, MotorMode, query_motor_mode

# 数据包大小
CTRL_DAT_SIZE = 15  # ControlData_t 大小减去CRC (17 - 2)
DATA_DAT_SIZE = 14  # MotorData_t 大小减去CRC (16 - 2)

# 包头
HEAD_BYTE_0 = 0xAA
HEAD_BYTE_1 = 0x55


class MotorCmd:
    """电机控制命令"""
    
    def __init__(self):
        self.motor_type: MotorType = MotorType.GO_M8010_6
        self.id: int = 0
        self.mode: int = 1  # FOC模式
        self.tau: float = 0.0  # 扭矩 (N.m)
        self.dq: float = 0.0    # 速度 (rad/s)
        self.q: float = 0.0     # 位置 (rad)
        self.kp: float = 0.0    # 位置刚度系数 (0.0-1.0)
        self.kd: float = 0.0    # 速度阻尼系数 (0.0-1.0)
    
    def pack(self) -> bytes:
        """
        将控制命令打包成二进制数据包
        
        Returns:
            打包后的数据包（17字节）
        """
        # 构建RIS_Mode_t (1字节)
        mode_byte = (self.id & 0x0F) | ((self.mode & 0x07) << 4)
        
        # 构建RIS_Comd_t (12字节)
        # tor_des: int16_t (q8) - 扭矩 * 256
        tor_des = int(round(self.tau * 256))
        tor_des = max(-32768, min(32767, tor_des))
        
        # spd_des: int16_t (q7) - 速度 * 128
        spd_des = int(round(self.dq * 128))
        spd_des = max(-32768, min(32767, spd_des))
        
        # pos_des: int32_t (q15) - 位置 * 32768
        pos_des = int(round(self.q * 32768))
        pos_des = max(-2147483648, min(2147483647, pos_des))
        
        # k_pos: uint16_t (q15) - 刚度系数 * 32768
        k_pos = int(round(max(0.0, min(1.0, self.kp)) * 32768))
        k_pos = max(0, min(65535, k_pos))
        
        # k_spd: uint16_t (q15) - 阻尼系数 * 32768
        k_spd = int(round(max(0.0, min(1.0, self.kd)) * 32768))
        k_spd = max(0, min(65535, k_spd))
        
        # 打包数据（不包括CRC）
        # 格式: 2字节头(BB) + 1字节模式(B) + 2字节扭矩(h) + 2字节速度(h) + 4字节位置(i) + 2字节k_pos(H) + 2字节k_spd(H)
        data = struct.pack(
            '<BBBhhiHH',  # 小端序: 2字节头 + 1字节模式 + 2字节扭矩 + 2字节速度 + 4字节位置 + 2字节k_pos + 2字节k_spd
            HEAD_BYTE_0,
            HEAD_BYTE_1,
            mode_byte,
            tor_des,
            spd_des,
            pos_des,
            k_pos,
            k_spd
        )
        
        # 计算CRC（不包括CRC字段本身）
        crc = crc_ccitt(0xffff, data)
        
        # 添加CRC
        packet = data + struct.pack('<H', crc)
        
        return packet


class MotorData:
    """电机反馈数据"""
    
    def __init__(self):
        self.motor_type: MotorType = MotorType.GO_M8010_6
        self.motor_id: int = 0
        self.mode: int = 0
        self.temp: int = 0          # 温度 (°C)
        self.merror: int = 0        # 错误标识
        self.tau: float = 0.0       # 扭矩 (N.m)
        self.dq: float = 0.0        # 速度 (rad/s)
        self.q: float = 0.0         # 位置 (rad)
        self.foot_force: int = 0    # 足端气压传感器数据
        self.correct: bool = False  # 数据是否有效
    
    def unpack(self, data: bytes) -> bool:
        """
        从二进制数据包解包电机反馈数据
        
        Args:
            data: 接收到的数据包（16字节）
            
        Returns:
            是否成功解包
        """
        if len(data) < 16:
            self.correct = False
            return False
        
        # 检查包头
        if data[0] != HEAD_BYTE_0 or data[1] != HEAD_BYTE_1:
            self.correct = False
            return False
        
        # 验证CRC
        crc_received = struct.unpack('<H', data[14:16])[0]
        crc_calculated = crc_ccitt(0xffff, data[:14])
        
        if crc_received != crc_calculated:
            self.correct = False
            return False
        
        # 解包数据
        # RIS_Fbk_t结构: torque(2) + speed(2) + pos(4) + temp(1) + [MError:3, force:12, none:1](2) = 11字节
        # 数据包结构: head(2) + mode(1) + RIS_Fbk_t(11) + CRC(2) = 16字节
        try:
            # 解包RIS_Fbk_t: torque(2) + speed(2) + pos(4) + temp(1) + error_force_bytes(2)
            torque, speed, pos, temp_byte, error_force_bytes = struct.unpack(
                '<hhiBH', data[3:14]  # 跳过head(2)和mode(1)，共11字节
            )
            
            # 解析mode_byte（在data[2]）
            mode_byte = data[2]
            self.motor_id = mode_byte & 0x0F
            self.mode = (mode_byte >> 4) & 0x07
            
            # 解析temp (int8_t)
            self.temp = struct.unpack('<b', bytes([temp_byte]))[0]
            
            # 解析error_force_bytes (uint16_t，2字节)
            # 位域布局：MError:3位(bit 0-2), force:12位(bit 3-14), none:1位(bit 15)
            self.merror = error_force_bytes & 0x07  # 低3位是MError
            self.foot_force = (error_force_bytes >> 3) & 0xFFF  # bit 3-14是force（12位）
            
            # 转换定点数到浮点数
            # torque: int16_t (q8) -> 除以256
            self.tau = torque / 256.0
            
            # speed: int16_t (q7) -> 除以128
            self.dq = speed / 128.0
            
            # pos: int32_t (q15) -> 除以32768
            self.q = pos / 32768.0
            
            self.correct = True
            return True
            
        except struct.error as e:
            self.correct = False
            return False
