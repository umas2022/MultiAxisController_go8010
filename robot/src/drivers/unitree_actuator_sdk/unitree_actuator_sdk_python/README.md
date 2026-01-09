# Unitree Motor SDK for Windows (Python)

这是一个纯Python实现的Unitree电机驱动SDK，专门为Windows系统设计，支持GO-M8010-6电机。

## 特性

- ✅ 纯Python实现，无需编译
- ✅ 支持Windows COM端口通信
- ✅ 支持GO-M8010-6电机
- ✅ 完整的CRC校验
- ✅ 简单易用的API

## 安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

或者直接安装pyserial：
```bash
pip install pyserial
```

## 使用方法

### 基本示例

```python
from unitree_motor import MotorCmd, MotorData, MotorMode, MotorType, SerialPort
from unitree_motor import query_motor_mode, query_gear_ratio

# 创建串口对象（Windows COM端口）
serial = SerialPort(port="COM11", baudrate=4000000)

# 创建命令和反馈对象
cmd = MotorCmd()
data = MotorData()

# 设置电机类型和模式
cmd.motor_type = MotorType.GO_M8010_6
data.motor_type = MotorType.GO_M8010_6
cmd.mode = query_motor_mode(MotorType.GO_M8010_6, MotorMode.FOC)
cmd.id = 0  # 电机ID

# 设置控制参数
cmd.q = 0.0                    # 位置 (rad)
cmd.dq = -6.28 * query_gear_ratio(MotorType.GO_M8010_6)  # 速度 (rad/s)
cmd.kp = 0.0                   # 位置刚度系数 (0.0-1.0)
cmd.kd = 0.01                  # 速度阻尼系数 (0.0-1.0)
cmd.tau = 0.0                  # 扭矩 (N.m)

# 发送命令并接收反馈
success = serial.send_recv(cmd, data)

if success and data.correct:
    print(f"位置: {data.q} rad")
    print(f"速度: {data.dq} rad/s")
    print(f"扭矩: {data.tau} N.m")
    print(f"温度: {data.temp} °C")

# 关闭串口
serial.close()
```

### 运行示例程序

```bash
python example_motor.py
```

## API文档

### SerialPort

串口通信类，用于与电机通信。

#### 构造函数

```python
SerialPort(
    port="COM11",           # 串口名称
    baudrate=4000000,       # 波特率
    timeout=0.02,           # 超时时间（秒）
    bytesize=8,             # 数据位
    parity='N',             # 校验位
    stopbits=1              # 停止位
)
```

#### 方法

- `send(data: bytes) -> int`: 发送数据
- `recv(length: int) -> bytes`: 接收数据
- `send_recv(cmd: MotorCmd, data: MotorData) -> bool`: 发送命令并接收反馈
- `close()`: 关闭串口

### MotorCmd

电机控制命令类。

#### 属性

- `motor_type`: 电机类型（MotorType.GO_M8010_6）
- `id`: 电机ID（0-14）
- `mode`: 电机模式（0=锁定, 1=FOC闭环, 2=编码器校准）
- `tau`: 期望扭矩 (N.m)
- `dq`: 期望速度 (rad/s)
- `q`: 期望位置 (rad)
- `kp`: 位置刚度系数 (0.0-1.0)
- `kd`: 速度阻尼系数 (0.0-1.0)

#### 方法

- `pack() -> bytes`: 打包成二进制数据包

### MotorData

电机反馈数据类。

#### 属性

- `motor_type`: 电机类型
- `motor_id`: 电机ID
- `mode`: 电机模式
- `temp`: 温度 (°C)
- `merror`: 错误标识（0=正常, 1=过热, 2=过流, 3=过压, 4=编码器故障）
- `tau`: 实际扭矩 (N.m)
- `dq`: 实际速度 (rad/s)
- `q`: 实际位置 (rad)
- `foot_force`: 足端气压传感器数据 (0-4095)
- `correct`: 数据是否有效（CRC校验通过）

#### 方法

- `unpack(data: bytes) -> bool`: 从二进制数据包解包

### 工具函数

- `query_motor_mode(motor_type: MotorType, motor_mode: MotorMode) -> int`: 查询电机模式值
- `query_gear_ratio(motor_type: MotorType) -> float`: 查询电机齿轮比（GO-M8010-6为6.0）

## 数据格式说明

### 定点数格式

- **q8**: 8位小数，值 = 整数 / 256
- **q7**: 7位小数，值 = 整数 / 128
- **q15**: 15位小数，值 = 整数 / 32768

### 数据包格式

- **控制数据包**: 17字节（2字节头 + 1字节模式 + 12字节命令 + 2字节CRC）
- **反馈数据包**: 16字节（2字节头 + 1字节模式 + 11字节反馈 + 2字节CRC）

## 注意事项

1. Windows下串口名称格式为 `COM11`（注意没有空格）
2. 默认波特率为4000000（4Mbps），确保串口支持此波特率
3. 电机ID范围：0-14，15表示广播（无返回）
4. 温度保护：90°C时触发温度保护
5. 控制循环建议间隔：200微秒（0.0002秒）

## 故障排除

### 串口打开失败

- 检查串口名称是否正确（Windows下为COM11格式）
- 检查串口是否被其他程序占用
- 检查串口驱动是否正常安装

### 数据接收失败

- 检查CRC校验是否通过（data.correct是否为True）
- 检查波特率设置是否正确
- 检查电机连接是否正常
- 检查电机ID是否匹配

### 电机无响应

- 检查电机电源是否接通
- 检查通信线是否连接正确
- 尝试重新校准编码器（MotorMode.CALIBRATE）

## 许可证

参考原始SDK的许可证。

## 联系方式

如有问题，请联系 support@unitree.com
