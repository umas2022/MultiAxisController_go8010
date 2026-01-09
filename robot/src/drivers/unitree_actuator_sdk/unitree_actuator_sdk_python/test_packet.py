"""
测试数据包打包和解包功能
"""

from unitree_motor import MotorCmd, MotorData


def test_packet_pack_unpack():
    """测试数据包打包和解包"""
    print("测试数据包打包和解包...")
    
    # 创建命令对象
    cmd = MotorCmd()
    cmd.id = 0
    cmd.mode = 1  # FOC模式
    cmd.tau = 1.5
    cmd.dq = 3.14
    cmd.q = 0.5
    cmd.kp = 0.8
    cmd.kd = 0.01
    
    # 打包
    packet = cmd.pack()
    print(f"打包后的数据包长度: {len(packet)} 字节 (应该是17字节)")
    print(f"数据包 (hex): {packet.hex()}")
    
    # 创建反馈数据对象并解包（模拟接收）
    data = MotorData()
    
    # 模拟一个反馈数据包（需要正确的格式）
    # 这里我们创建一个测试数据包
    import struct
    from unitree_motor.crc import crc_ccitt
    
    HEAD_BYTE_0 = 0xAA
    HEAD_BYTE_1 = 0x55
    
    # 构建测试反馈数据包
    mode_byte = 0x01  # ID=0, mode=1
    torque = int(1.5 * 256)  # q8
    speed = int(3.14 * 128)  # q7
    pos = int(0.5 * 32768)   # q15
    temp = 25  # 25°C
    error_force = 0x0000  # MError=0, force=0, none=0
    
    test_data = struct.pack(
        '<BBhhiBH',
        HEAD_BYTE_0,
        HEAD_BYTE_1,
        mode_byte,
        torque,
        speed,
        pos,
        temp,
        error_force
    )
    
    # 计算CRC
    crc = crc_ccitt(0xffff, test_data)
    test_packet = test_data + struct.pack('<H', crc)
    
    print(f"\n测试反馈数据包长度: {len(test_packet)} 字节 (应该是16字节)")
    print(f"测试数据包 (hex): {test_packet.hex()}")
    
    # 解包
    success = data.unpack(test_packet)
    
    if success:
        print("\n解包成功!")
        print(f"电机ID: {data.motor_id}")
        print(f"模式: {data.mode}")
        print(f"扭矩: {data.tau:.4f} N.m")
        print(f"速度: {data.dq:.4f} rad/s")
        print(f"位置: {data.q:.4f} rad")
        print(f"温度: {data.temp} °C")
        print(f"错误码: {data.merror}")
        print(f"足端力: {data.foot_force}")
    else:
        print("\n解包失败!")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_packet_pack_unpack()
