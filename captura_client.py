import socket
import numpy as np
import cv2
import mss
import struct
import time

class ScreenCaptureClient:
    """
    屏幕捕获客户端
    用于捕获指定屏幕区域并通过socket将图像流传输到服务器
    
    特点：
    - 支持自定义捕获区域
    - 自动图像压缩和调整大小
    - 断线重连机制
    - 可配置的传输帧率
    """
    
    def __init__(self, host="localhost", port=6666):
        self.host = host
        self.port = port
        # 默认捕获区域设置，可根据需要调整
        self.monitor = {
            "top": 100,     # 距离屏幕顶部的像素
            "left": 400,    # 距离屏幕左侧的像素
            "width": 1600,  # 捕获宽度
            "height": 1000  # 捕获高度
        }
        
    def capture_screen(self):
        """
        捕获屏幕指定区域
        返回: ndarray 格式的图像帧
        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            # 将图像缩放至标准大小以优化传输
            frame = cv2.resize(frame, (800, 600))
            return frame
        
    def send_frame(self, client_socket, frame):
        """
        将图像帧编码并通过socket发送
        参数:
            client_socket: socket连接对象
            frame: 要发送的图像帧
        """
        _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        img_bytes = img_encoded.tobytes()
        img_size = len(img_bytes)
        
        # 先发送数据大小，再发送实际数据
        size_pack = struct.pack('Q', img_size)
        client_socket.sendall(size_pack)
        client_socket.sendall(img_bytes)
        
    def start_streaming(self):
        """
        启动屏幕捕获和传输流程
        包含自动重连机制和异常处理
        """
        client_socket = None
        try:
            while True:  # 添加外层循环实现断线重连
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((self.host, self.port))
                    print("成功连接到服务器")
                    
                    while True:
                        frame = self.capture_screen()
                        self.send_frame(client_socket, frame)
                        time.sleep(0.03)  # 约33FPS，可根据需要调整
                        
                except ConnectionError:
                    print("连接断开，5秒后尝试重新连接...")
                    time.sleep(5)
                    continue
                    
        except KeyboardInterrupt:
            print("手动停止传输")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if client_socket:
                client_socket.close()

if __name__ == "__main__":
    client = ScreenCaptureClient()
    client.start_streaming()