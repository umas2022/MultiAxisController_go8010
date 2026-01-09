"""
串口和电机连接诊断工具
"""

import time
import serial
from unitree_motor import MotorCmd, MotorData, MotorMode, MotorType, SerialPort
from unitree_motor import query_motor_mode, query_gear_ratio


def test_serial_port(port="COM11", baudrate=4000000):
    """测试串口基本功能"""
    print(f"\n{'='*60}")
    print(f"测试串口: {port}, 波特率: {baudrate}")
    print(f"{'='*60}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
            dsrdtr=False,
            rtscts=False,
            xonxoff=False
        )
        ser.rts = False
        ser.dtr = False
        
        print(f"✓ 串口打开成功")
        print(f"  串口名称: {ser.name}")
        print(f"  波特率: {ser.baudrate}")
        print(f"  数据位: {ser.bytesize}")
        print(f"  校验位: {ser.parity}")
        print(f"  停止位: {ser.stopbits}")
        
        # 清空缓冲区
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # 检查是否有数据在总线上
        time.sleep(0.1)
        if ser.in_waiting > 0:
            print(f"\n⚠ 警告: 输入缓冲区中有 {ser.in_waiting} 字节数据")
            data = ser.read(ser.in_waiting)
            print(f"  数据 (hex): {data.hex()}")
        else:
            print(f"\n✓ 输入缓冲区为空（正常）")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"✗ 串口打开失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_motor_communication(port="COM11", motor_id=0):
    """测试电机通信"""
    print(f"\n{'='*60}")
    print(f"测试电机通信: COM端口={port}, 电机ID={motor_id}")
    print(f"{'='*60}")
    
    try:
        serial_port = SerialPort(port=port, baudrate=4000000)
        
        cmd = MotorCmd()
        data = MotorData()
        
        cmd.motor_type = MotorType.GO_M8010_6
        data.motor_type = MotorType.GO_M8010_6
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        cmd.id = motor_id
        
        # 设置简单的控制参数
        cmd.q = 0.0
        cmd.dq = 0.0
        cmd.kp = 0.0
        cmd.kd = 0.01
        cmd.tau = 0.0
        
        print(f"\n尝试与电机通信（ID={motor_id}）...")
        print("发送命令并等待响应...")
        
        # 尝试多次通信
        success_count = 0
        for i in range(5):
            success = serial_port.send_recv(cmd, data, debug=True)
            if success and data.correct:
                success_count += 1
                print(f"\n✓ 第 {i+1} 次通信成功!")
                print(f"  电机ID: {data.motor_id}")
                print(f"  位置: {data.q:.4f} rad")
                print(f"  速度: {data.dq:.4f} rad/s")
                print(f"  温度: {data.temp} °C")
                break
            else:
                print(f"\n✗ 第 {i+1} 次通信失败")
            time.sleep(0.1)
        
        serial_port.close()
        
        if success_count > 0:
            print(f"\n✓ 电机通信测试成功!")
            return True
        else:
            print(f"\n✗ 电机通信测试失败")
            print(f"\n可能的原因:")
            print(f"  1. 电机未上电")
            print(f"  2. 电机ID不正确（当前ID={motor_id}）")
            print(f"  3. 串口连接问题")
            print(f"  4. 波特率不匹配")
            print(f"  5. 电机处于其他模式（需要先进入FOC模式）")
            return False
            
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def scan_motor_ids(port="COM11"):
    """扫描总线上所有可能的电机ID"""
    print(f"\n{'='*60}")
    print(f"扫描电机ID (COM端口: {port})")
    print(f"{'='*60}")
    
    try:
        serial_port = SerialPort(port=port, baudrate=4000000)
        
        cmd = MotorCmd()
        data = MotorData()
        
        cmd.motor_type = MotorType.GO_M8010_6
        data.motor_type = MotorType.GO_M8010_6
        cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
        
        found_motors = []
        
        for motor_id in range(16):  # ID范围 0-15
            cmd.id = motor_id
            cmd.q = 0.0
            cmd.dq = 0.0
            cmd.kp = 0.0
            cmd.kd = 0.01
            cmd.tau = 0.0
            
            success = serial_port.send_recv(cmd, data, debug=False)
            if success and data.correct:
                found_motors.append(motor_id)
                print(f"✓ 发现电机 ID={motor_id}")
                print(f"  位置: {data.q:.4f} rad")
                print(f"  速度: {data.dq:.4f} rad/s")
                print(f"  温度: {data.temp} °C")
            
            time.sleep(0.05)  # 每个ID之间等待50ms
        
        serial_port.close()
        
        if found_motors:
            print(f"\n✓ 共发现 {len(found_motors)} 个电机: {found_motors}")
        else:
            print(f"\n✗ 未发现任何电机")
        
        return found_motors
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    print("="*60)
    print("Unitree 电机连接诊断工具")
    print("="*60)
    
    port = "COM11"
    motor_id = 0
    
    # 1. 测试串口基本功能
    if not test_serial_port(port):
        print("\n请检查串口连接和配置")
        return
    
    # 2. 测试电机通信
    if not test_motor_communication(port, motor_id):
        print("\n尝试扫描所有可能的电机ID...")
        found = scan_motor_ids(port)
        if found:
            print(f"\n建议: 使用发现的电机ID之一: {found}")
        else:
            print("\n请检查:")
            print("  1. 电机是否已上电")
            print("  2. 串口线是否正确连接")
            print("  3. 波特率是否正确（应该是4000000）")
            print("  4. 电机是否处于正确的模式")
        return
    
    print("\n" + "="*60)
    print("✓ 所有测试通过！电机连接正常")
    print("="*60)


if __name__ == "__main__":
    main()
