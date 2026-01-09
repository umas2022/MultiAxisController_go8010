# 快速开始指南

## 安装

1. 安装依赖：
```bash
pip install pyserial
```

或者使用requirements.txt：
```bash
pip install -r requirements.txt
```

2. （可选）安装为Python包：
```bash
pip install -e .
```

## 基本使用

### 1. 导入模块

```python
from unitree_motor import MotorCmd, MotorData, MotorMode, MotorType, SerialPort
from unitree_motor import query_motor_mode, query_gear_ratio
```

### 2. 创建串口连接

```python
# Windows下使用COM端口
serial = SerialPort(port="COM11", baudrate=4000000)
```

### 3. 创建命令和反馈对象

```python
cmd = MotorCmd()
data = MotorData()

# 设置电机类型
cmd.motor_type = MotorType.GO_M8010_6
data.motor_type = MotorType.GO_M8010_6
```

### 4. 配置电机参数

```python
# 设置电机模式为FOC闭环控制
cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
cmd.id = 0  # 电机ID

# 设置控制参数
cmd.q = 0.0                    # 位置 (rad)
cmd.dq = -6.28 * query_gear_ratio(MotorType.GO_M8010_6)  # 速度 (rad/s)
cmd.kp = 0.0                   # 位置刚度系数
cmd.kd = 0.01                  # 速度阻尼系数
cmd.tau = 0.0                  # 扭矩 (N.m)
```

### 5. 发送命令并接收反馈

```python
import time

while True:
    # 发送命令并接收反馈
    success = serial.send_recv(cmd, data)
    
    if success and data.correct:
        print(f"位置: {data.q:.4f} rad")
        print(f"速度: {data.dq:.4f} rad/s")
        print(f"扭矩: {data.tau:.4f} N.m")
        print(f"温度: {data.temp} °C")
    
    time.sleep(0.0002)  # 200微秒
```

### 6. 关闭串口

```python
serial.close()
```

## 运行示例

运行示例程序：
```bash
python example_motor.py
```

## 测试数据包功能

测试数据包打包和解包：
```bash
python test_packet.py
```

## 常见问题

### Q: 串口打开失败怎么办？

A: 
1. 检查串口名称是否正确（Windows下为 `COM11` 格式，注意没有空格）
2. 检查串口是否被其他程序占用
3. 检查设备管理器中串口是否正常识别

### Q: 数据接收失败怎么办？

A:
1. 检查 `data.correct` 是否为 `True`（CRC校验通过）
2. 检查波特率设置是否正确（默认4000000）
3. 检查电机连接和电源
4. 检查电机ID是否匹配

### Q: 如何修改串口参数？

A: 在创建SerialPort时指定参数：
```python
serial = SerialPort(
    port="COM11",
    baudrate=4000000,
    timeout=0.02,
    bytesize=8,
    parity='N',
    stopbits=1
)
```

## 注意事项

1. **串口名称**: Windows下使用 `COM11` 格式（注意大小写）
2. **波特率**: 默认4000000（4Mbps），确保串口支持此波特率
3. **控制频率**: 建议控制循环间隔200微秒（0.0002秒）
4. **电机ID**: 范围0-14，15表示广播（无返回）
5. **温度保护**: 90°C时触发温度保护
