"""
Serial port communication for Unitree motors on Windows
"""
import serial
import time
from typing import Optional, Tuple


class SerialPort:
    """
    Serial port communication class for Unitree motors on Windows
    """
    
    def __init__(self, port_name: str = "COM11", baudrate: int = 4000000, timeout: float = 0.02):
        """
        Initialize serial port
        
        Args:
            port_name: Serial port name (e.g., "COM11")
            baudrate: Baud rate for communication (default 4000000 for high-speed motor comm)
            timeout: Read timeout in seconds
        """
        self.port_name = port_name
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None
        self.is_open = False
        
        self._open_port()
    
    def _open_port(self):
        """Open the serial port"""
        try:
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                # Additional settings that might help with compatibility
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            # Additional configuration for better compatibility
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            print(f"Serial port {self.port_name} opened successfully")
        except Exception as e:
            print(f"Failed to open serial port {self.port_name}: {e}")
            raise
    
    def close(self):
        """Close the serial port"""
        if self.serial_port and self.is_open:
            self.serial_port.close()
            self.is_open = False
            print(f"Serial port {self.port_name} closed")
    
    def send(self, data: bytes) -> bool:
        """
        Send data to the serial port
        
        Args:
            data: Data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.serial_port.reset_output_buffer()  # Clear output buffer before sending
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()  # Ensure data is sent immediately
            return bytes_written == len(data)
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def recv(self, size: int = 16) -> Optional[bytes]:
        """
        Receive data from the serial port
        
        Args:
            size: Number of bytes to read
            
        Returns:
            Received data or None if error
        """
        try:
            data = self.serial_port.read(size)
            return data if data else None
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def send_recv(self, send_data: bytes, recv_size: int = 16, delay: float = 0.0002) -> Optional[bytes]:
        """
        Send data and receive response
        
        Args:
            send_data: Data to send
            recv_size: Size of expected response
            delay: Delay between send and receive in seconds
            
        Returns:
            Received response or None if error
        """
        # Clear buffers before communication
        self.serial_port.reset_input_buffer()
        self.serial_port.reset_output_buffer()
        
        # Send data
        if not self.send(send_data):
            return None
        
        # Small delay to allow motor to process
        time.sleep(delay)
        
        # Receive response
        return self.recv(recv_size)
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.is_open:
            self.close()
