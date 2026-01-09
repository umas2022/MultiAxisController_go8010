import time
import sys
import os

# 添加SDK库路径
sdk_path = os.path.join(os.path.dirname(__file__), 'unitree_actuator_sdk/lib')
sys.path.append(sdk_path)

try:
    from unitree_actuator_sdk import *
except ImportError:
    print("无法导入 unitree_actuator_sdk，请确保已编译并安装了Python绑定")
    raise


class MotorDriver8010:
    """
    GO-M8010-6电机驱动器封装类
    简化了原始SDK的复杂性，提供了更易用的接口
    """
    
    def __init__(self, port="/dev/ttyUSB0"):
        """
        初始化电机驱动器
        
        Args:
            port (str): 串口设备路径，默认为/dev/ttyUSB0
        """
        self.serial = SerialPort(port)
        self.cmd = MotorCmd()
        self.data = MotorData()
        
        # 设置电机类型为GO-M8010-6
        self.cmd.motorType = MotorType.GO_M8010_6
        self.data.motorType = MotorType.GO_M8010_6
        
        # 设置默认工作模式
        self.cmd.mode = queryMotorMode(MotorType.GO_M8010_6, MotorMode.FOC)
        
        # 默认参数
        self.default_kp = 0.0
        self.default_kd = 0.01
        self.gear_ratio = queryGearRatio(MotorType.GO_M8010_6)
        
    def set_motor_id(self, motor_id):
        """
        设置目标电机ID
        
        Args:
            motor_id (int): 电机ID (0-14)，15为广播模式
        """
        self.cmd.id = motor_id
    
    def enable_motor(self):
        """启用电机（进入FOC模式）"""
        self.cmd.mode = queryMotorMode(MotorType.GO_M8010_6, MotorMode.FOC)
    
    def disable_motor(self):
        """禁用电机（进入刹车模式）"""
        self.cmd.mode = queryMotorMode(MotorType.GO_M8010_6, MotorMode.BRAKE)
    
    def send_command(self, position=0.0, velocity=0.0, kp=None, kd=None, torque=0.0):
        """
        发送控制命令到电机
        
        Args:
            position (float): 目标位置 (rad)
            velocity (float): 目标速度 (rad/s)
            kp (float): 位置增益 (None则使用默认值)
            kd (float): 速度增益 (None则使用默认值)
            torque (float): 前馈力矩 (Nm)
        
        Returns:
            dict: 包含电机反馈数据的字典
        """
        # 设置控制参数
        self.cmd.q = position
        self.cmd.dq = velocity
        self.cmd.kp = kp if kp is not None else self.default_kp
        self.cmd.kd = kd if kd is not None else self.default_kd
        self.cmd.tau = torque
        
        # 发送命令并接收反馈
        self.serial.sendRecv(self.cmd, self.data)
        
        # 返回反馈数据
        feedback = {
            'position': self.data.q,
            'velocity': self.data.dq,
            'torque': self.data.tau,
            'temperature': self.data.temp,
            'error': self.data.merror
        }
        
        return feedback
    
    def position_control(self, position, kp=None, kd=None):
        """
        位置控制模式
        
        Args:
            position (float): 目标位置 (rad)
            kp (float): 位置增益
            kd (float): 速度增益
        
        Returns:
            dict: 电机反馈数据
        """
        return self.send_command(position=position, kp=kp, kd=kd)
    
    def velocity_control(self, velocity, kd=None):
        """
        速度控制模式
        
        Args:
            velocity (float): 目标速度 (rad/s)
            kd (float): 速度增益
        
        Returns:
            dict: 电机反馈数据
        """
        return self.send_command(velocity=velocity, kp=0.0, kd=kd if kd is not None else 0.1)
    
    def torque_control(self, torque):
        """
        力矩控制模式
        
        Args:
            torque (float): 目标力矩 (Nm)
        
        Returns:
            dict: 电机反馈数据
        """
        return self.send_command(torque=torque, kp=0.0, kd=0.0)
    
    def brake_mode(self):
        """切换到刹车模式"""
        self.cmd.mode = queryMotorMode(MotorType.GO_M8010_6, MotorMode.BRAKE)
        # 发送刹车命令
        self.send_command(kp=0.0, kd=0.0, torque=0.0)
    
    def calibrate_mode(self):
        """切换到校准模式"""
        self.cmd.mode = queryMotorMode(MotorType.GO_M8010_6, MotorMode.CALIBRATE)
    
    def get_gear_ratio(self):
        """
        获取减速比
        
        Returns:
            float: 减速比
        """
        return self.gear_ratio
    
    def continuous_read(self, callback=None, interval=0.002):
        """
        连续读取电机数据
        
        Args:
            callback (function): 数据回调函数，接收反馈数据作为参数
            interval (float): 读取间隔时间（秒）
        """
        try:
            while True:
                feedback = self.send_command()
                
                if callback:
                    callback(feedback)
                else:
                    print(f"位置: {feedback['position']:.3f}, "
                          f"速度: {feedback['velocity']:.3f}, "
                          f"力矩: {feedback['torque']:.3f}, "
                          f"温度: {feedback['temperature']}°C, "
                          f"错误: {feedback['error']}")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n连续读取已停止")
    
    def set_default_params(self, kp, kd):
        """
        设置默认控制参数
        
        Args:
            kp (float): 默认位置增益
            kd (float): 默认速度增益
        """
        self.default_kp = kp
        self.default_kd = kd


# 示例用法
if __name__ == "__main__":
    # 创建电机驱动实例
    motor_driver = MotorDriver8010("/dev/ttyUSB0")
    
    # 设置电机ID
    motor_driver.set_motor_id(0)
    
    print("开始电机控制测试...")
    print("每200微秒发送一次命令")
    
    try:
        for i in range(10000):  # 测试10000次循环
            # 发送控制命令：位置为0，速度为6.28 rad/s
            feedback = motor_driver.send_command(
                position=0.0, 
                velocity=6.28 * motor_driver.get_gear_ratio(),
                kp=0.0,
                kd=0.01,
                torque=0.0
            )
            
            # 每隔100次打印一次反馈数据
            if i % 100 == 0:
                print(f"\n第{i}次:")
                print(f"位置: {feedback['position']:.3f}")
                print(f"速度: {feedback['velocity']:.3f}")
                print(f"温度: {feedback['temperature']}°C")
                print(f"错误: {feedback['error']}")
            
            # 200微秒延迟
            time.sleep(0.0002)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    
    finally:
        # 程序结束前关闭电机
        motor_driver.brake_mode()
        print("电机已停机")