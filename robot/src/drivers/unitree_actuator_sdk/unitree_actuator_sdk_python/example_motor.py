"""
GO-M8010-6 电机控制示例程序
电机连接在 COM11，ID=0
"""

import time
from unitree_motor import MotorCmd, MotorData, MotorMode, MotorType, SerialPort
from unitree_motor import query_motor_mode, query_gear_ratio


def main():
    # 创建串口对象（Windows COM端口）
    serial = SerialPort(port="COM11", baudrate=4000000)
    
    # 创建命令和反馈对象
    cmd = MotorCmd()
    data = MotorData()
    
    # 设置电机类型
    cmd.motor_type = MotorType.GO_M8010_6
    data.motor_type = MotorType.GO_M8010_6
    
    # 设置电机模式为FOC闭环控制
    cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
    cmd.id = 0  # 电机ID
    
    print("开始电机控制循环...")
    print("按 Ctrl+C 停止")
    print("\n提示: 如果持续出现'数据接收失败'，请修改代码将 debug=True 以查看详细信息\n")
    
    try:
        loop_count = 0
        while True:
            # 设置控制参数
            cmd.q = 0.0                    # 位置 (rad)
            cmd.dq = -6.28 * query_gear_ratio(MotorType.GO_M8010_6)  # 速度 (rad/s)
            cmd.kp = 0.0                   # 位置刚度系数
            cmd.kd = 0.01                  # 速度阻尼系数
            cmd.tau = 0.0                  # 扭矩 (N.m)
            
            # 前3次循环启用调试模式
            debug = (loop_count < 3)
            success = serial.send_recv(cmd, data, debug=debug)
            loop_count += 1
            
            if success and data.correct:
                print("\n" + "="*50)
                print(f"电机ID: {data.motor_id}")
                print(f"位置 (q): {data.q:.4f} rad")
                print(f"速度 (dq): {data.dq:.4f} rad/s")
                print(f"扭矩 (tau): {data.tau:.4f} N.m")
                print(f"温度: {data.temp} °C")
                print(f"错误码: {data.merror}")
                print(f"足端力: {data.foot_force}")
                print("="*50)
            else:
                print("数据接收失败或CRC校验错误")
            
            # 等待200微秒（0.0002秒）
            time.sleep(0.0002)
            
    except KeyboardInterrupt:
        print("\n程序停止")
    finally:
        serial.close()


if __name__ == "__main__":
    main()
