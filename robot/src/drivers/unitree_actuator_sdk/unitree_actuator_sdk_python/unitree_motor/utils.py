"""
工具函数
"""

from enum import IntEnum


class MotorType(IntEnum):
    """电机类型"""
    GO_M8010_6 = 0


class MotorMode(IntEnum):
    """电机模式"""
    BRAKE = 0      # 锁定
    FOC = 1        # FOC闭环
    CALIBRATE = 2  # 编码器校准


def query_motor_mode(motor_type: MotorType, motor_mode: MotorMode) -> int:
    """
    查询电机模式值
    
    Args:
        motor_type: 电机类型
        motor_mode: 电机模式
        
    Returns:
        模式值（用于数据包）
    """
    if motor_type == MotorType.GO_M8010_6:
        if motor_mode == MotorMode.BRAKE:
            return 0
        elif motor_mode == MotorMode.FOC:
            return 1
        elif motor_mode == MotorMode.CALIBRATE:
            return 2
    return 0


def query_gear_ratio(motor_type: MotorType) -> float:
    """
    查询电机齿轮比
    
    Args:
        motor_type: 电机类型
        
    Returns:
        齿轮比
    """
    if motor_type == MotorType.GO_M8010_6:
        return 6.0  # GO-M8010-6 的齿轮比
    return 1.0
