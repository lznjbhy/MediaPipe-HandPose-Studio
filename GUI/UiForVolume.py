import sys
import time
import os
import cv2
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox, QProgressBar,
                             QFileDialog, QSlider, QStyle, QSizePolicy, QGroupBox)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QUrl, QSize
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class VolumeControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能手势音量控制")
        self.setGeometry(180, 65, 1570, 905)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #333;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
                border-radius: 4px;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a86e8, stop:1 #3a76d8);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)

        # 初始化变量
        self.wCam, self.hCam = 640, 480
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.pTime = 0
        self.detector = HandDetector(detectionCon=0.7)

        # 音频设置
        self.setup_audio()

        # 媒体播放器
        self.media_player = QMediaPlayer()
        self.current_music = "无音乐"

        self.camera_on = False

        self.init_ui()

        # 周期性地更新摄像头画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def setup_audio(self):
        # 系统音量设置
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]
        self.vol = 0
        self.volBar = 400
        self.volPer = 0

        # 获取当前系统音量
        current_vol = self.volume.GetMasterVolumeLevel()
        self.volPer = int(np.interp(current_vol, [self.minVol, self.maxVol], [0, 100]))

    def init_ui(self):
        # 主窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 左侧面板 - 摄像头和控制
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        # 摄像头显示区域
        camera_group = QGroupBox("摄像头视图")
        camera_group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }"
                                   "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        camera_layout = QVBoxLayout(camera_group)

        self.camera_feed = QLabel()
        self.camera_feed.setMinimumSize(self.wCam, self.hCam)
        self.camera_feed.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: #e9ecef;")
        self.camera_feed.setAlignment(Qt.AlignCenter)
        self.camera_feed.setText("摄像头已关闭")

        camera_layout.addWidget(self.camera_feed)
        left_panel.addWidget(camera_group)

        # 摄像头控制按钮
        control_group = QGroupBox("控制面板")
        control_group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }"
                                    "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        control_layout = QVBoxLayout(control_group)

        camera_controls = QHBoxLayout()
        self.btn_start_camera = QPushButton("打开摄像头")
        self.btn_start_camera.setFont(QFont("SimHei", 10, QFont.Bold))
        self.btn_start_camera.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_stop_camera = QPushButton("关闭摄像头")
        self.btn_stop_camera.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.btn_stop_camera.setFont(QFont("SimHei", 10, QFont.Bold))
        self.btn_start_camera.clicked.connect(self.start_camera)
        self.btn_stop_camera.clicked.connect(self.stop_camera)

        camera_controls.addWidget(self.btn_start_camera)
        camera_controls.addWidget(self.btn_stop_camera)

        control_layout.addLayout(camera_controls)
        left_panel.addWidget(control_group)

        # 右侧面板 - 音频和音量控制
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # 音乐选择
        music_group = QGroupBox("音乐播放器")
        music_group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }"
                                  "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        music_layout = QVBoxLayout(music_group)

        music_controls = QHBoxLayout()
        self.btn_select_music = QPushButton("选择音乐文件")
        self.btn_select_music.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btn_select_music.clicked.connect(self.select_music)

        self.btn_play_music = QPushButton("播放")
        self.btn_play_music.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play_music.clicked.connect(self.play_music)

        self.btn_pause_music = QPushButton("暂停")
        self.btn_pause_music.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_pause_music.clicked.connect(self.pause_music)

        music_controls.addWidget(self.btn_select_music)
        music_controls.addWidget(self.btn_play_music)
        music_controls.addWidget(self.btn_pause_music)

        self.current_music_label = QLabel("当前播放: " + self.current_music)
        self.current_music_label.setStyleSheet("font-weight: bold;")
        self.current_music_label.setAlignment(Qt.AlignCenter)

        self.music_progress = QProgressBar()
        self.music_progress.setMinimum(0)
        self.music_progress.setMaximum(100)
        self.music_progress.setValue(0)
        self.music_progress.setTextVisible(False)

        music_layout.addWidget(self.current_music_label)
        music_layout.addWidget(self.music_progress)
        music_layout.addLayout(music_controls)
        right_panel.addWidget(music_group)

        # 系统音量控制
        volume_group = QGroupBox("系统音量控制")
        volume_group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }"
                                   "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        volume_layout = QVBoxLayout(volume_group)

        volume_display = QHBoxLayout()
        volume_icon = QLabel()
        volume_icon.setPixmap(self.style().standardIcon(QStyle.SP_MediaVolume).pixmap(QSize(24, 24)))
        volume_display.addWidget(volume_icon)

        self.volume_bar = QProgressBar()
        self.volume_bar.setMinimum(0)
        self.volume_bar.setMaximum(100)
        self.volume_bar.setValue(self.volPer)
        self.volume_bar.setTextVisible(True)
        self.volume_bar.setFormat("%v%")
        volume_display.addWidget(self.volume_bar)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.volPer)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.valueChanged.connect(self.set_volume)

        volume_layout.addLayout(volume_display)
        volume_layout.addWidget(self.volume_slider)
        right_panel.addWidget(volume_group)

        # 性能指标
        stats_group = QGroupBox("帧率")
        stats_group.setStyleSheet("QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }"
                                  "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        stats_layout = QVBoxLayout(stats_group)

        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a86e8;")

        stats_layout.addWidget(self.fps_label)
        right_panel.addWidget(stats_group)

        # 添加面板到主布局
        main_layout.addLayout(left_panel, 2)  # 左侧占2/3空间
        main_layout.addLayout(right_panel, 1)  # 右侧占1/3空间

    def start_camera(self):
        if not self.camera_on:
            self.camera_on = True
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.wCam)
            self.cap.set(4, self.hCam)
            self.timer.start(10)  # 每10ms更新一次
            self.btn_start_camera.setEnabled(False)
            self.btn_stop_camera.setEnabled(True)

    def stop_camera(self):
        if self.camera_on:
            self.camera_on = False
            self.timer.stop()
            self.cap.release()
            self.camera_feed.setText("摄像头已关闭")
            self.camera_feed.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: #e9ecef;")
            self.btn_start_camera.setEnabled(True)
            self.btn_stop_camera.setEnabled(False)

    def select_music(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音乐文件", "", "音频文件 (*.mp3 *.wav *.ogg *.flac);;所有文件 (*)"
        )
        if file_path:
            self.current_music = os.path.basename(file_path)
            self.current_music_label.setText("当前播放: " + self.current_music)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.music_progress.setValue(0)

    def play_music(self):
        if self.current_music != "无音乐":
            self.media_player.play()

    def pause_music(self):
        self.media_player.pause()

    def set_volume(self, value):
        self.volPer = value
        self.volume_bar.setValue(value)
        vol = np.interp(value, [0, 100], [self.minVol, self.maxVol])
        self.volume.SetMasterVolumeLevel(vol, None)

    def update_frame(self):
        success, img = self.cap.read()
        if success:
            # 镜像翻转图像
            img = cv2.flip(img, 1)

            # 处理图像与手部检测器
            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                # 手部跟踪逻辑
                x1, y1 = lmList[4][1], lmList[4][2]  # 拇指指尖
                x2, y2 = lmList[8][1], lmList[8][2]  # 食指指尖
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # 两指中间点

                # 绘制关键点和连线
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

                # 计算两指间距离
                length = math.hypot(x2 - x1, y2 - y1)

                # 音量转换 (距离范围30-240对应音量0-100%)
                self.vol = np.interp(length, [30, 240], [self.minVol, self.maxVol])
                self.volBar = np.interp(length, [30, 240], [400, 150])
                self.volPer = int(np.interp(length, [30, 240], [0, 100]))

                # 限制音量范围
                self.volPer = max(0, min(100, self.volPer))

                # 设置系统音量
                self.volume.SetMasterVolumeLevel(self.vol, None)

                # 更新UI音量条和滑块
                self.volume_bar.setValue(self.volPer)
                self.volume_slider.setValue(self.volPer)

                # 当距离很小时显示绿色圆圈表示静音状态
                if length < 50:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            # 添加音量可视化到图像
            cv2.rectangle(img, (50, 150), (85, 400), (42, 134, 232), 3)
            cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (42, 134, 232), cv2.FILLED)
            cv2.putText(img, f'{self.volPer}%', (40, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (42, 134, 232), 2)

            # 计算并显示FPS
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime

            # 更新UI中的FPS标签
            self.fps_label.setText(f"FPS: {int(fps)}")

            # 在图像上显示FPS
            cv2.putText(img, f'FPS: {int(fps)}', (40, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (42, 134, 232), 2)

            # 转换为Qt格式并显示
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_feed.setPixmap(pixmap)

    def closeEvent(self, event):
        # 应用关闭时清理资源
        if self.camera_on:
            self.timer.stop()
            self.cap.release()
        event.accept()


class HandDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, trackCon=0.5):
        import mediapipe as mp
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mp_draw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, handLms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = VolumeControlApp()
    window.show()
    sys.exit(app.exec_())
