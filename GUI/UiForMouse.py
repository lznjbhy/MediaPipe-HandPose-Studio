import sys
import cv2
import numpy as np
import time
import autopy
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor, QIcon, QPainter, QBrush, QPen
from Mouse.Track import handDetector


class GradientFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QColor(227, 242, 253)
        painter.fillRect(self.rect(), QBrush(gradient))
        super().paintEvent(event)


class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #42A5F5;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                padding: 8px 16px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #2196F3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            QPushButton:pressed {
                transform: translateY(0);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            }
            QPushButton:disabled {
                background-color: #BBDEFB;
                color: #607D8B;
                cursor: not-allowed;
            }
        """)


class ModeIndicator(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(80)
        self.setFont(QFont("Arial", 28, QFont.Bold))
        self.setStyleSheet("""
            QLabel {
                color: #263238;
                border-radius: 10px;
                padding: 10px;
                background-color: rgba(227, 242, 253, 0.8);
                border: 2px solid rgba(66, 165, 245, 0.7);
            }
        """)


class FPSIndicator(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(80)
        self.setFont(QFont("Arial", 28, QFont.Bold))
        self.setStyleSheet("""
            QLabel {
                color: #263238;
                border-radius: 10px;
                padding: 10px;
                background-color: rgba(227, 242, 253, 0.8);
                border: 2px solid rgba(76, 175, 80, 0.7);
            }
        """)


class GestureMouseControlUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能手势鼠标控制系统")
        self.setGeometry(180, 65, 1570, 905)

        # 设置全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECEFF1;
            }
            QLabel {
                color: #263238;
            }
            QFrame {
                border-radius: 10px;
            }
        """)

        # 初始化变量
        self.wCam, self.hCam = 800, 600
        self.frameR = 160
        self.smoothening = 7
        self.pTime = 0
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.wScr, self.hScr = autopy.screen.size()
        self.detector = handDetector(maxHands=1)
        self.cap = None
        self.is_camera_open = False
        self.current_mode = "无"
        self.current_fps = 0

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 创建标题
        title_label = QLabel("智能手势鼠标控制系统")
        title_label.setFont(QFont("Arial", 45, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # 创建上部布局（摄像头和信息面板）
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # 左侧摄像头画面
        camera_frame = GradientFrame()
        camera_frame.setMinimumSize(800, 600)
        camera_layout = QVBoxLayout(camera_frame)

        self.camera_feed = QLabel()
        self.camera_feed.setAlignment(Qt.AlignCenter)
        self.camera_feed.setText("点击下方按钮打开摄像头")
        self.camera_feed.setFont(QFont("Arial", 20))
        self.camera_feed.setStyleSheet("color: #607D8B;")

        camera_layout.addWidget(self.camera_feed)

        # 右侧信息面板
        info_frame = GradientFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(20)
        info_layout.setContentsMargins(20, 20, 20, 20)

        # 模式说明
        mode_desc_frame = QFrame()
        mode_desc_frame.setStyleSheet("background-color: rgba(227, 242, 253, 0.8); border-radius: 10px;")
        mode_desc_layout = QVBoxLayout(mode_desc_frame)
        mode_desc_layout.setContentsMargins(15, 15, 15, 15)

        mode_desc_title = QLabel("手势控制说明")
        mode_desc_title.setFont(QFont("Arial", 18, QFont.Bold))
        mode_desc_title.setStyleSheet("color: #1976D2; border-bottom: 1px solid #1976D2; padding-bottom: 5px;")

        mode_items = [
            "单指抬起: 鼠标移动",
            "双指抬起: 左键点击",
            "三指抬起: 右键点击"
        ]

        mode_desc_text = QLabel("\n".join(mode_items))
        mode_desc_text.setFont(QFont("Arial", 14))
        mode_desc_text.setStyleSheet("color: #263238;")

        mode_desc_layout.addWidget(mode_desc_title)
        mode_desc_layout.addWidget(mode_desc_text)

        # 状态显示区域
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: rgba(227, 242, 253, 0.8); border-radius: 10px;")
        status_layout = QGridLayout(status_frame)
        status_layout.setSpacing(15)
        status_layout.setContentsMargins(15, 15, 15, 15)

        # 当前模式显示
        current_mode_label = QLabel("当前模式:")
        current_mode_label.setFont(QFont("Arial", 16))
        current_mode_label.setStyleSheet("color: #263238;")

        self.mode_value = ModeIndicator("无")

        # 当前帧率显示
        current_fps_label = QLabel("当前帧率:")
        current_fps_label.setFont(QFont("Arial", 16))
        current_fps_label.setStyleSheet("color: #263238;")

        self.fps_value = FPSIndicator("0")

        status_layout.addWidget(current_mode_label, 0, 0)
        status_layout.addWidget(self.mode_value, 0, 1)
        status_layout.addWidget(current_fps_label, 1, 0)
        status_layout.addWidget(self.fps_value, 1, 1)

        info_layout.addWidget(mode_desc_frame)
        info_layout.addWidget(status_frame)

        top_layout.addWidget(camera_frame, 3)
        top_layout.addWidget(info_frame, 1)

        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        self.btn_open_camera = RoundedButton("打开摄像头")
        self.btn_close_camera = RoundedButton("关闭摄像头")
        self.btn_exit = RoundedButton("退出系统")

        self.btn_open_camera.clicked.connect(self.open_camera)
        self.btn_close_camera.clicked.connect(self.close_camera)
        self.btn_exit.clicked.connect(self.close)

        bottom_layout.addWidget(self.btn_open_camera)
        bottom_layout.addWidget(self.btn_close_camera)
        bottom_layout.addWidget(self.btn_exit)

        # 将布局添加到主布局
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # 创建定时器用于更新摄像头画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 初始化界面状态
        self.btn_close_camera.setEnabled(False)

    def open_camera(self):
        if not self.is_camera_open:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.wCam)
            self.cap.set(4, self.hCam)

            if self.cap.isOpened():
                self.is_camera_open = True
                self.timer.start(10)  # 约100 FPS的刷新率
                self.btn_open_camera.setEnabled(False)
                self.btn_close_camera.setEnabled(True)
                self.camera_feed.setStyleSheet("")
            else:
                self.camera_feed.setText("无法打开摄像头")
                self.camera_feed.setStyleSheet("color: #D32F2F; font-size: 24px;")

    def close_camera(self):
        if self.is_camera_open:
            self.timer.stop()
            self.cap.release()
            self.is_camera_open = False
            self.camera_feed.setText("点击下方按钮打开摄像头")
            self.camera_feed.setFont(QFont("Arial", 20))
            self.camera_feed.setStyleSheet("color: #607D8B;")
            self.btn_open_camera.setEnabled(True)
            self.btn_close_camera.setEnabled(False)
            self.mode_value.setText("无")
            self.fps_value.setText("0")

    def update_frame(self):
        if self.is_camera_open:
            # 1. 获取图像帧并处理
            success, img = self.cap.read()
            if not success:
                return

            img = cv2.flip(img, 1)  # 水平翻转，使镜像更直观
            img = self.detector.findHands(img)
            lmList, bbox = self.detector.findPosition(img)

            # 设置默认模式
            current_mode = "移动"
            mode_color = (66, 165, 245)  # 淡蓝色，表示移动模式

            # 2. 获取手指位置
            if len(lmList) != 0:
                # 食指和中指的坐标
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # 3. 检查哪些手指竖起
                fingers = self.detector.fingersUp()

                # 4. 绘制操作区域
                cv2.rectangle(img, (self.frameR, self.frameR),
                              (self.wCam - self.frameR, self.hCam - self.frameR),
                              (66, 165, 245), 2)

                # 5. 判断模式并执行相应操作
                if fingers[1] == 1 and fingers[2] == 0:
                    # 移动模式
                    current_mode = "移动"
                    mode_color = (66, 165, 245)  # 淡蓝色

                    # 转换坐标
                    x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
                    y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))

                    # 平滑值
                    self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                    self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening

                    # 移动鼠标
                    autopy.mouse.move(self.clocX, self.clocY)
                    cv2.circle(img, (x1, y1), 15, (66, 165, 245), cv2.FILLED)
                    self.plocX, self.plocY = self.clocX, self.clocY

                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                    # 左键点击模式
                    current_mode = "左键"
                    mode_color = (76, 175, 80)  # 绿色

                    # 计算两指之间的距离
                    length, img, lineInfo = self.detector.findDistance(8, 12, img)

                    # 如果距离小于阈值，执行点击
                    if length < 20:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   15, (76, 175, 80), cv2.FILLED)
                        autopy.mouse.click()

                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                    # 右键点击模式
                    current_mode = "右键"
                    mode_color = (255, 152, 0)  # 橙色
                    autopy.mouse.click(button=autopy.mouse.Button.RIGHT, delay=0)

            # 更新模式显示
            self.mode_value.setText(current_mode)
            # 根据不同模式设置不同颜色
            if current_mode == "移动":
                self.mode_value.setStyleSheet("""
                    QLabel {
                        color: #263238;
                        border-radius: 10px;
                        padding: 10px;
                        background-color: rgba(227, 242, 253, 0.8);
                        border: 2px solid rgba(66, 165, 245, 0.7);
                    }
                """)
            elif current_mode == "左键":
                self.mode_value.setStyleSheet("""
                    QLabel {
                        color: #263238;
                        border-radius: 10px;
                        padding: 10px;
                        background-color: rgba(227, 242, 253, 0.8);
                        border: 2px solid rgba(76, 175, 80, 0.7);
                    }
                """)
            elif current_mode == "右键":
                self.mode_value.setStyleSheet("""
                    QLabel {
                        color: #263238;
                        border-radius: 10px;
                        padding: 10px;
                        background-color: rgba(227, 242, 253, 0.8);
                        border: 2px solid rgba(255, 152, 0, 0.7);
                    }
                """)

            # 6. 计算并显示帧率
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if self.pTime > 0 else 0
            self.pTime = cTime
            self.fps_value.setText(f"{int(fps)}")

            # 7. 将OpenCV图像转换为Qt图像并显示
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_feed.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.camera_feed.width(), self.camera_feed.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, event):
        # 关闭窗口时释放资源
        if self.is_camera_open:
            self.close_camera()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestureMouseControlUI()
    window.show()
    sys.exit(app.exec_())
