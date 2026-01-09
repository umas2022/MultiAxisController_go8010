"""
Windows串口通信类
"""

import serial
import time
from typing import Optional
from .motor import MotorCmd, MotorData


class SerialPort:
    """串口通信类，用于Windows COM端口"""
    
    def __init__(
        self,
        port: str = "COM11",
        baudrate: int = 4000000,
        timeout: float = 0.02,  # 20ms超时
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: int = serial.STOPBITS_ONE,
        force_rts: bool = False,
        force_dtr: bool = False,
    ):
        """
        初始化串口
        
        Args:
            port: 串口名称，Windows下如 "COM11"
            baudrate: 波特率，默认4000000
            timeout: 超时时间（秒）
            bytesize: 数据位
            parity: 校验位
            stopbits: 停止位
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.force_rts = force_rts
        self.force_dtr = force_dtr
        
        self._ser: Optional[serial.Serial] = None
        self._open()
    
    def _open(self):
        """打开串口"""
        try:
            self._ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                write_timeout=self.timeout,
                dsrdtr=False,  # 禁用DSR/DTR流控
                rtscts=False,  # 禁用RTS/CTS流控
                xonxoff=False,  # 禁用软件流控
                inter_byte_timeout=0.01,
            )
            # Windows下可能需要设置RTS和DTR
            self._ser.rts = self.force_rts
            self._ser.dtr = self.force_dtr
            
            # 清空输入输出缓冲区
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
            
            # 等待串口稳定
            time.sleep(0.1)
            
            actual_baud = getattr(self._ser, "baudrate", None)
            print(f"串口 {self.port} 打开成功，波特率: {self.baudrate}")
            if actual_baud and actual_baud != self.baudrate:
                print(f"⚠ 实际波特率: {actual_baud} (与请求的 {self.baudrate} 不一致)")
            print(f"串口配置: {self.bytesize}位数据位, {self.parity}校验, {self.stopbits}停止位")
        except serial.SerialException as e:
            raise RuntimeError(f"无法打开串口 {self.port}: {e}")
    
    def close(self):
        """关闭串口"""
        if self._ser and self._ser.is_open:
            self._ser.close()
            print(f"串口 {self.port} 已关闭")
    
    def send(self, data: bytes) -> int:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            实际发送的字节数
        """
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("串口未打开")
        
        return self._ser.write(data)
    
    def recv(self, length: int) -> bytes:
        """
        接收数据
        
        Args:
            length: 要接收的字节数
            
        Returns:
            接收到的数据
        """
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("串口未打开")
        
        data = self._ser.read(length)
        return data
    
    def send_recv(self, cmd: MotorCmd, data: MotorData, debug: bool = False) -> bool:
        """
        发送命令并接收反馈
        
        Args:
            cmd: 电机控制命令
            data: 用于存储反馈数据的MotorData对象
            debug: 是否输出调试信息
            
        Returns:
            是否成功接收并解析数据
        """
        # 打包命令
        cmd_packet = cmd.pack()
        
        if debug:
            print(f"发送数据包 (hex): {cmd_packet.hex()}")
            print(f"发送数据包长度: {len(cmd_packet)} 字节")
        
        # 清空输入缓冲区，避免读取到旧数据
        self._ser.reset_input_buffer()
        
        # 发送命令
        bytes_sent = self.send(cmd_packet)
        if debug:
            print(f"已发送 {bytes_sent} 字节")
            # 确保数据已发送
            self._ser.flush()
        
        # 等待电机响应（对于高速通信，需要足够的时间）
        # 根据波特率计算：16字节 * 10位/字节 / 4000000 bps ≈ 40微秒
        # 但实际需要更多时间用于处理延迟
        time.sleep(0.001)  # 1毫秒，给电机足够的响应时间
        
        # 尝试接收反馈（16字节）
        # 使用read_until或直接read，但需要确保能接收到完整数据包
        recv_data = b''
        max_attempts = 50  # 增加尝试次数
        start_time = time.time()
        
        for attempt in range(max_attempts):
            # 检查是否有数据可读
            if self._ser.in_waiting > 0:
                chunk = self.recv(min(16 - len(recv_data), self._ser.in_waiting))
                if chunk:
                    recv_data += chunk
                    if len(recv_data) >= 16:
                        break
            
            # 如果已经等待超过超时时间，退出
            if time.time() - start_time > self.timeout:
                break
                
            time.sleep(0.0001)  # 每次尝试间隔100微秒
        
        # 如果还没收到完整数据，再尝试一次完整读取
        if len(recv_data) < 16:
            remaining = self.recv(16 - len(recv_data))
            if remaining:
                recv_data += remaining
        
        if debug:
            print(f"接收数据长度: {len(recv_data)} 字节 (尝试 {attempt + 1} 次)")
            if len(recv_data) > 0:
                print(f"接收数据 (hex): {recv_data.hex()}")
                if len(recv_data) >= 2:
                    print(f"包头: 0x{recv_data[0]:02X} 0x{recv_data[1]:02X} (期望: 0xAA 0x55)")
        
        if len(recv_data) < 16:
            if debug:
                print(f"数据不完整: 只接收到 {len(recv_data)} 字节，需要 16 字节")
            data.correct = False
            return False
        
        # 如果数据包不完整或包头不对，尝试查找正确的数据包起始位置
        if recv_data[0] != 0xAA or recv_data[1] != 0x55:
            # 尝试在接收到的数据中查找包头
            header_pos = recv_data.find(b'\xAA\x55')
            if header_pos >= 0 and len(recv_data) >= header_pos + 16:
                recv_data = recv_data[header_pos:header_pos + 16]
                if debug:
                    print(f"找到包头位置: {header_pos}, 使用偏移后的数据")
            else:
                if debug:
                    print("未找到有效的包头")
                data.correct = False
                return False
        
        # 解包反馈数据
        success = data.unpack(recv_data)
        
        if debug and not success:
            if recv_data[0] != 0xAA or recv_data[1] != 0x55:
                print("包头错误")
            else:
                # 检查CRC
                import struct
                from .crc import crc_ccitt
                crc_received = struct.unpack('<H', recv_data[14:16])[0]
                crc_calculated = crc_ccitt(0xffff, recv_data[:14])
                print(f"CRC错误: 接收={crc_received:04X}, 计算={crc_calculated:04X}")
        
        return success
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()
