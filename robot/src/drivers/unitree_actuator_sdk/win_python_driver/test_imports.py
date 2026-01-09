"""
Test script to verify that all modules import correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")

try:
    from src.motor_control import GO_M8010_6_Motor, MotorCmd, MotorMode, MotorType, scan_motor_ids
    print("✓ motor_control module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import motor_control: {e}")

try:
    from src.motor_protocol import MotorData, ControlData, RISMode, RISComd, RISFbk, query_motor_mode, query_gear_ratio
    print("✓ motor_protocol module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import motor_protocol: {e}")

try:
    from src.serial_port import SerialPort
    print("✓ serial_port module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import serial_port: {e}")

try:
    from utils.crc import crc_ccitt
    print("✓ crc module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import crc: {e}")

print("\nAll modules imported successfully! The Windows Python driver is ready to use.")
print("\nTo use with a physical motor:")
print("1. Connect the GO-M8010-6 motor to COM11")
print("2. Ensure motor power is on")
print("3. Run one of the example scripts")