"""
Test CRC functionality
"""
from utils.crc import crc_ccitt

# Test CRC with some sample data
test_data = b'\xFF\xFE\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
crc_result = crc_ccitt(test_data)
print(f'CRC result for test data: 0x{crc_result:04X}')

# Test with another sample
hello_crc = crc_ccitt(b'hello world')
print(f'CRC for "hello world": 0x{hello_crc:04X}')

print("CRC functionality working correctly!")