import socket
import cv2
import numpy as np
import struct
from ultralytics import YOLO

class DetectionServer:
    """
    目标检测服务器
    接收图像流并使用YOLO模型进行实时目标检测
    
    特点：
    - 支持实时视频流处理
    - 集成YOLO目标检测
    - 自动窗口管理
    - 健壮的错误处理
    """
    
    def __init__(self, host="localhost", port=6666, model_path='yolov8n.pt'):
        self.host = host
        self.port = port
        self.buffer_size = 8192
        # 初始化YOLO模型
        self.model = YOLO(model_path)
        
    def receive_frame(self, client_socket):
        """
        接收并解码图像帧
        参数:
            client_socket: 客户端socket连接
        返回:
            解码后的图像帧，如果接收失败返回None
        """
        try:
            # 首先接收图像大小信息
            size_pack = client_socket.recv(struct.calcsize('Q'))
            if not size_pack:
                return None
            
            img_size = struct.unpack('Q', size_pack)[0]
            
            # 分块接收图像数据
            img_data = b''
            while len(img_data) < img_size:
                remaining = img_size - len(img_data)
                chunk = client_socket.recv(min(remaining, self.buffer_size))
                if not chunk:
                    return None
                img_data += chunk
            
            # 将接收到的字节数据转换为图像
            img_arr = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            return frame
        except socket.error:
            return None
            
    def process_frame(self, frame):
        """
        使用YOLO模型处理图像
        参数:
            frame: 输入图像
        返回:
            处理后的图像（带有检测框和标签）
        """
        if frame is None:
            return None
        results = self.model(frame)
        return results[0].plot()
        
    def start_server(self):
        """
        启动检测服务器
        处理客户端连接并实时显示检测结果
        """
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print("等待客户端连接...")
            
            # 创建显示窗口
            cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Object Detection', cv2.WND_PROP_TOPMOST, 1)
            cv2.moveWindow('Object Detection', 0, 0)
            
            while True:  # 添加外层循环支持客户端断开后等待新连接
                client_socket, addr = server_socket.accept()
                print(f"客户端 {addr} 已连接")
                
                try:
                    while True:
                        frame = self.receive_frame(client_socket)
                        if frame is None:
                            break
                            
                        processed_frame = self.process_frame(frame)
                        cv2.imshow('Object Detection', processed_frame)
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                            
                except Exception as e:
                    print(f"处理过程中发生错误: {e}")
                finally:
                    client_socket.close()
                    print("客户端断开连接，等待新的连接...")
                    
        except KeyboardInterrupt:
            print("服务器停止运行")
        finally:
            server_socket.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    server = DetectionServer()
    server.start_server() 