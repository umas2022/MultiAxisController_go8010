"""
CRC calculation functions for Unitree motor communication
"""
from typing import List


def generate_crc_table() -> List[int]:
    """Generate CRC-CCITT lookup table"""
    table = []
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
        table.append(crc)
    return table


# Pre-compute CRC table
CRC_TABLE = generate_crc_table()


def crc_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    """
    Calculate CRC-CCITT for the given data
    
    Args:
        data: Input data bytes
        initial: Initial CRC value (default 0xFFFF)
    
    Returns:
        CRC-CCITT value
    """
    crc = initial
    for byte in data:
        # Get the upper 8 bits of CRC and XOR with the current byte
        table_index = ((crc >> 8) ^ byte) & 0xFF
        # Shift CRC 8 bits and XOR with table value
        crc = ((crc << 8) ^ CRC_TABLE[table_index]) & 0xFFFF
    return crc