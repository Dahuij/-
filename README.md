# -Real-time Screen Capture and Object Detection System
该项目实现了一个实时视频传输与处理系统，包括两个主要组件： 1. 传输端（ScreenCaptureClient）： 使用mss库捕获指定区域的屏幕图像，压缩为JPEG格式，并通过TCP连接发送到接收端。 2.接收端（VideoProcessingServer）： 接收传输端发送的图像数据，解码为图像帧，并使用YOLO模型进行对象检测，最后在窗口中显示处理后的图像。
## 功能特点

- 实时屏幕区域捕获
- 自动图像压缩和优化
- 使用YOLO进行实时目标检测
- 支持断线自动重连
- 可配置的捕获区域和传输帧率
- 健壮的错误处理机制

## 系统要求

- Python 3.7+
- OpenCV
- Ultralytics YOLO
- MSS (屏幕捕获库)
- NumPy

## 安装
bash
pip install opencv-python ultralytics mss numpy
## 使用方法
1. 首先启动检测服务器：detection_server.py
2. 然后启动屏幕捕获客户端：capture_client.py

## 配置说明

### 客户端配置

可以在 `ScreenCaptureClient` 类的初始化方法中修改以下参数：

- 捕获区域设置（top, left, width, height）
- 服务器地址和端口
- 传输帧率

### 服务器配置

可以在 `DetectionServer` 类中修改：

- 监听地址和端口
- YOLO模型路径
- 缓冲区大小

## 注意事项

- 可能需要根据实际硬件性能调整图像大小和帧率
- 建议在使用GPU的环境中运行以获得更好的检测性能

## 贡献

欢迎提交Issue和Pull Request！
