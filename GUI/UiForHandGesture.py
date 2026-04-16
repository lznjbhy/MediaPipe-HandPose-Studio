import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QPalette, QColor
from Finger.GestureRecognitionModule import GestureRecognizer


class GestureRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.cap = None
        self.recognizer = GestureRecognizer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.gesture_images = self.load_gesture_images()
        print("加载的手势图像:", self.gesture_images.keys())

        # 用于存储当前显示的图片对象
        self.current_camera_pixmap = None
        self.current_gesture_pixmap = None

    def initUI(self):
        self.setWindowTitle("手势识别系统")
        self.setGeometry(180, 65, 1500, 905)

        # 设置整体背景颜色
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(240, 240, 240))
        self.setPalette(palette)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 标题样式
        title_label = QLabel("手势识别系统")
        title_label.setFont(QFont("SimHei", 50, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        left_layout = QVBoxLayout()
        content_layout.addLayout(left_layout, 2)

        # 摄像头框架样式
        self.camera_frame = QFrame()
        self.camera_frame.setFrameShape(QFrame.Box)
        self.camera_frame.setLineWidth(1)
        self.camera_frame.setFixedSize(840, 580)
        self.camera_frame.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
        camera_layout = QVBoxLayout(self.camera_frame)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setScaledContents(False)
        camera_layout.addWidget(self.camera_label)
        left_layout.addWidget(self.camera_frame)

        button_layout = QHBoxLayout()
        self.open_camera_btn = QPushButton("打开摄像头")
        self.open_camera_btn.setFixedSize(180, 40)
        self.open_camera_btn.setFont(QFont("SimHei", 10, QFont.Bold))
        self.open_camera_btn.clicked.connect(self.start_camera)
        self.open_camera_btn.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px;")

        self.close_camera_btn = QPushButton("关闭摄像头")
        self.close_camera_btn.setFixedSize(180, 40)
        self.close_camera_btn.setFont(QFont("SimHei", 10, QFont.Bold))
        self.close_camera_btn.clicked.connect(self.stop_camera)
        self.close_camera_btn.setEnabled(False)
        self.close_camera_btn.setStyleSheet(
            "background-color: #f44336; color: white; border: none; border-radius: 5px;")

        button_layout.addWidget(self.open_camera_btn)
        button_layout.addWidget(self.close_camera_btn)
        left_layout.addLayout(button_layout)

        right_layout = QVBoxLayout()
        content_layout.addLayout(right_layout, 1)

        result_title = QLabel("识别结果")
        result_title.setFont(QFont("SimHei", 15))
        result_title.setAlignment(Qt.AlignCenter)
        result_title.setStyleSheet("color: #333;")
        right_layout.addWidget(result_title)
        result_title.setFixedSize(700, 70)
        self.result_frame = QFrame()
        self.result_frame.setFrameShape(QFrame.Box)
        self.result_frame.setLineWidth(1)
        self.result_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_frame.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")

        result_frame_layout = QVBoxLayout(self.result_frame)

        self.result_label = QLabel("无画面")
        self.result_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        result_frame_layout.addWidget(self.result_label)

        right_layout.addWidget(self.result_frame)
        right_layout.addSpacing(15)

        gesture_title = QLabel("对应手势")
        gesture_title.setFont(QFont("SimHei", 15))
        gesture_title.setAlignment(Qt.AlignCenter)
        gesture_title.setStyleSheet("color: #333;")
        right_layout.addWidget(gesture_title)

        self.gesture_frame = QFrame()
        self.gesture_frame.setFrameShape(QFrame.Box)
        self.gesture_frame.setLineWidth(1)
        self.gesture_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gesture_frame.setFixedSize(700, 439)
        self.gesture_frame.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
        gesture_frame_layout = QVBoxLayout(self.gesture_frame)

        self.gesture_label = QLabel()
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gesture_label.setScaledContents(False)
        gesture_frame_layout.addWidget(self.gesture_label)

        right_layout.addWidget(self.gesture_frame, stretch=2)
        right_layout.addStretch(1)  # 保持原有的弹性空间，确保手势框位置不变

        # 添加退出系统按钮
        exit_btn_layout = QHBoxLayout()
        self.exit_btn = QPushButton("退出系统")
        self.exit_btn.setFixedSize(100, 40)
        self.exit_btn.setFont(QFont("SimHei", 10, QFont.Bold))
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setStyleSheet("background-color: #2196F3; color: white; border: none; border-radius: 5px;")
        exit_btn_layout.addStretch()
        exit_btn_layout.addWidget(self.exit_btn)
        exit_btn_layout.addStretch()

        right_layout.addLayout(exit_btn_layout)
        right_layout.addSpacing(50)  # 距离底部100px的间距

    # 以下方法保持不变...
    def load_gesture_images(self):
        """从 resources 文件夹加载手势图像，对应结果为 '1'-'10', 'ok', 'unknown'"""
        gesture_dict = {}
        for i in range(1, 11):
            path = os.path.join("resources", f"gesture_{i}.png")
            if os.path.exists(path):
                gesture_dict[str(i)] = QPixmap(path)
            else:
                print(f"缺失图片: {path}")
        for key in ["ok", "unknown"]:
            path = os.path.join("resources", f"gesture_{key}.png")
            if os.path.exists(path):
                gesture_dict[key] = QPixmap(path)
            else:
                print(f"缺失图片: {path}")
        return gesture_dict

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        if self.cap.isOpened():
            self.open_camera_btn.setEnabled(False)
            self.close_camera_btn.setEnabled(True)
            self.timer.start(30)
        else:
            self.result_label.setText("摄像头打开失败")

    def stop_camera(self):
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.open_camera_btn.setEnabled(True)
        self.close_camera_btn.setEnabled(False)
        self.camera_label.clear()
        self.result_label.setText("无画面")
        self.gesture_label.clear()

        # 释放图片资源
        self.current_camera_pixmap = None
        self.current_gesture_pixmap = None

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        processed_img, gesture = self.recognizer.process_image(img, print_result=False)
        rgb_image = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 优化图片处理逻辑
        if self.current_camera_pixmap:
            del self.current_camera_pixmap

        self.current_camera_pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = self.current_camera_pixmap.scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation)
        self.camera_label.setPixmap(scaled_pixmap)

        # 统一识别结果
        gesture_str = str(gesture).strip().lower()
        self.result_label.setText(gesture_str if gesture_str != "unknown" else "?")

        # 更新手势图片
        if gesture_str in self.gesture_images:
            if self.current_gesture_pixmap:
                del self.current_gesture_pixmap

            self.current_gesture_pixmap = self.gesture_images[gesture_str]
            scaled_gesture = self.current_gesture_pixmap.scaled(
                self.gesture_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
            self.gesture_label.setPixmap(scaled_gesture)
        else:
            self.gesture_label.clear()

    def resizeEvent(self, event):
        # 只在窗口大小改变时重新缩放当前图片
        if self.current_camera_pixmap:
            scaled_pixmap = self.current_camera_pixmap.scaled(
                self.camera_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)

        if self.current_gesture_pixmap:
            scaled_gesture = self.current_gesture_pixmap.scaled(
                self.gesture_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
            self.gesture_label.setPixmap(scaled_gesture)

        super().resizeEvent(event)

    def closeEvent(self, event):
        self.stop_camera()
        # 清理资源
        if hasattr(self, 'gesture_images'):
            for pixmap in self.gesture_images.values():
                if not pixmap.isNull():
                    pixmap = QPixmap()  # 释放资源
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestureRecognitionApp()
    window.show()
    sys.exit(app.exec_())