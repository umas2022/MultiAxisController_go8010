#include <stdio.h>
#include <unistd.h>
#include "serialPort/SerialPort.h"
#include "unitreeMotor/unitreeMotor.h"

int main() {
    // 在WSL中，串口设备通常映射为 /dev/ttyS* 或 /dev/ttyUSB*
    // 请根据实际情况修改串口名称
    SerialPort serial("/dev/ttyUSB0");  // 或者尝试 "/dev/ttyS4" 等
    
    printf("开始扫描总线上所有电机ID...\n");
    
    // 尝试扫描ID 0-15 (通常电机ID范围)
    for(int id = 0; id <= 15; id++) {
        MotorCmd cmd;
        MotorData data;
        
        cmd.motorType = MotorType::GO_M8010_6;
        data.motorType = MotorType::GO_M8010_6;
        cmd.mode = queryMotorMode(MotorType::GO_M8010_6, MotorMode::FOC);
        cmd.id = id;
        cmd.kp = 0.0;
        cmd.kd = 0.01;
        cmd.q = 0.0;
        cmd.dq = 0.0;
        cmd.tau = 0.0;
        
        // 尝试与特定ID的电机通信
        bool success = serial.sendRecv(&cmd, &data);
        
        if(success) {
            printf("发现电机 - ID: %d\n", id);
            printf("  位置: %.3f\n", data.q);
            printf("  速度: %.3f\n", data.dq);
            printf("  温度: %d°C\n", data.temp);
            printf("  错误: %d\n", data.merror);
        } else {
            printf("ID %d: 无响应\n", id);
        }
        
        usleep(50000); // 50ms delay between each query
    }
    
    printf("扫描完成\n");
    return 0;
}