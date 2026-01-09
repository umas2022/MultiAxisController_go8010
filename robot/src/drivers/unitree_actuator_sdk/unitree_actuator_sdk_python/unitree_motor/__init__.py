"""
Unitree Motor SDK for Windows (Python)
支持 GO-M8010-6 电机
"""

from .motor import MotorCmd, MotorData
from .serial_port import SerialPort
from .utils import MotorMode, MotorType, query_motor_mode, query_gear_ratio

__version__ = "1.0.0"
__all__ = [
    'MotorCmd',
    'MotorData', 
    'MotorMode',
    'MotorType',
    'SerialPort',
    'query_motor_mode',
    'query_gear_ratio'
]
