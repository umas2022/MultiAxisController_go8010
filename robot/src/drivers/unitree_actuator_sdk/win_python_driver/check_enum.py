#!/usr/bin/env python
"""Check enum values and function behavior"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.motor_protocol import MotorType, MotorMode, query_motor_mode, MotorStatus

def main():
    print("Checking enum values...")
    print(f"MotorType.GO_M8010_6 = {MotorType.GO_M8010_6}")
    print(f"MotorType.A1 = {MotorType.A1}")
    print(f"MotorType.B1 = {MotorType.B1}")
    
    print(f"MotorMode.FOC = {MotorMode.FOC}")
    print(f"MotorMode.BRAKE = {MotorMode.BRAKE}")
    print(f"MotorMode.CALIBRATE = {MotorMode.CALIBRATE}")
    
    print(f"MotorStatus.LOCKED = {MotorStatus.LOCKED}")
    print(f"MotorStatus.FOC_CLOSED_LOOP = {MotorStatus.FOC_CLOSED_LOOP}")
    print(f"MotorStatus.ENCODER_CALIBRATION = {MotorStatus.ENCODER_CALIBRATION}")
    
    print("\nTesting equality...")
    print(f"MotorType.GO_M8010_6 == MotorType.GO_M8010_6: {MotorType.GO_M8010_6 == MotorType.GO_M8010_6}")
    print(f"MotorMode.FOC == MotorMode.FOC: {MotorMode.FOC == MotorMode.FOC}")
    
    print("\nTesting query_motor_mode function...")
    
    # Test each combination
    result1 = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    print(f"query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC) = {result1}")
    
    result2 = query_motor_mode(MotorType.GO_M8010_6, MotorMode.BRAKE)
    print(f"query_motor_mode(MotorType.GO_M8010_6, MotorMode.BRAKE) = {result2}")
    
    result3 = query_motor_mode(MotorType.GO_M8010_6, MotorMode.CALIBRATE)
    print(f"query_motor_mode(MotorType.GO_M8010_6, MotorMode.CALIBRATE) = {result3}")
    
    # Also test invalid combination
    result4 = query_motor_mode(MotorType.A1, MotorMode.FOC)  # Different motor type
    print(f"query_motor_mode(MotorType.A1, MotorMode.FOC) = {result4}")
    
    print("\nTesting MotorStatus values...")
    print(f"MotorStatus.LOCKED.value = {MotorStatus.LOCKED.value}")
    print(f"MotorStatus.FOC_CLOSED_LOOP.value = {MotorStatus.FOC_CLOSED_LOOP.value}")
    print(f"MotorStatus.ENCODER_CALIBRATION.value = {MotorStatus.ENCODER_CALIBRATION.value}")

if __name__ == "__main__":
    main()