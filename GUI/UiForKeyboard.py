import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from KeyBoard.Track import HandDetector
from time import sleep
from pynput.keyboard import Controller


class VirtualKeyboardGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
            QLabel {
                color: #334155;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #4338ca;
                transform: translateY(-2px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            QPushButton:pressed {
                transform: translateY(0);
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            }
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-size: 18px;
                color: #1e293b;
                background-color: white;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            }
        """)

        # 窗口设置
        self.setWindowTitle("虚拟键盘系统")
        self.setGeometry(180, 65, 1570, 905)

        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 添加标题
        title_label = QLabel("虚拟键盘模块")
        title_font = QFont("Arial", 28, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #1e3a8a;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        """)
        main_layout.addWidget(title_label)

        # 创建分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e2e8f0;")
        main_layout.addWidget(line)

        # 上部分布局（摄像头和文本区域）
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        main_layout.addLayout(top_layout, 8)  # 占80%高度

        # 摄像头显示区域 - 占比70%
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            background-color: #1e293b;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        """)
        camera_layout = QVBoxLayout(camera_frame)
        camera_title = QLabel("摄像头画面")
        camera_title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 500;
            margin: 10px 0 10px 20px;
        """)
        camera_layout.addWidget(camera_title)

        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(800, 600)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #0f172a; border-radius: 8px; margin: 0 20px 20px 20px;")
        camera_layout.addWidget(self.camera_label)

        top_layout.addWidget(camera_frame, 7)  # 占70%宽度

        # 文本编辑区域 - 占比30%
        text_frame = QFrame()
        text_frame.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        """)
        text_layout = QVBoxLayout(text_frame)
        text_title = QLabel("输入文本")
        text_title.setStyleSheet("""
            color: #1e293b;
            font-size: 18px;
            font-weight: 500;
            margin: 10px 0 10px 20px;
        """)
        text_layout.addWidget(text_title)

        self.text_edit = QTextEdit()
        self.text_edit.setMinimumHeight(600)
        self.text_edit.setStyleSheet("""
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            font-size: 20px;
            color: #1e293b;
            background-color: #f8fafc;
            margin: 0 20px 20px 20px;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
        """)
        text_layout.addWidget(self.text_edit)

        top_layout.addWidget(text_frame, 3)  # 占30%宽度

        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        main_layout.addLayout(bottom_layout, 1)  # 占10%高度

        # 创建按钮
        self.open_camera_btn = QPushButton("打开摄像头")
        self.close_camera_btn = QPushButton("关闭摄像头")
        self.clear_text_btn = QPushButton("清空文本")
        self.save_text_btn = QPushButton("保存文本")
        self.exit_btn = QPushButton("退出系统")

        # 设置按钮样式
        self.open_camera_btn.setStyleSheet("background-color: #22c55e;")
        self.close_camera_btn.setStyleSheet("background-color: #f97316;")
        self.clear_text_btn.setStyleSheet("background-color: #3b82f6;")
        self.save_text_btn.setStyleSheet("background-color: #8b5cf6;")
        self.exit_btn.setStyleSheet("background-color: #ef4444;")

        # 添加按钮到底部布局
        bottom_layout.addWidget(self.open_camera_btn)
        bottom_layout.addWidget(self.close_camera_btn)
        bottom_layout.addWidget(self.clear_text_btn)
        bottom_layout.addWidget(self.save_text_btn)
        bottom_layout.addWidget(self.exit_btn)

        # 摄像头相关变量
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 连接按钮事件
        self.open_camera_btn.clicked.connect(self.open_camera)
        self.close_camera_btn.clicked.connect(self.close_camera)
        self.clear_text_btn.clicked.connect(self.clear_text)
        self.save_text_btn.clicked.connect(self.save_text)
        self.exit_btn.clicked.connect(self.close_application)

        # 初始化虚拟键盘相关组件
        self.detector = HandDetector(detectionCon=0.6)
        self.keyboard = Controller()
        self.keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                     ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                     ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
        self.button_list = []

        # 初始化虚拟键盘按钮
        for i in range(len(self.keys)):
            for j, key in enumerate(self.keys[i]):
                self.button_list.append(Button([100 * j + 50, 100 * i + 50], key))

        # 当前文本跟踪
        self.final_text = ""

        # 初始状态
        self.close_camera_btn.setEnabled(False)

    def open_camera(self):
        """打开摄像头"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 1280)  # 设置宽度
            self.cap.set(4, 720)  # 设置高度

            if not self.cap.isOpened():
                QMessageBox.critical(self, "错误", "无法打开摄像头!")
                self.cap = None
                return

            self.timer.start(30)  # 30ms刷新一次，约33FPS
            self.open_camera_btn.setEnabled(False)
            self.close_camera_btn.setEnabled(True)

            # 添加按钮状态变化动画效果
            self.animate_button_state(self.open_camera_btn, False)
            self.animate_button_state(self.close_camera_btn, True)

    def close_camera(self):
        """关闭摄像头"""
        if self.cap is not None:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.camera_label.clear()
            self.camera_label.setText("摄像头已关闭")
            self.camera_label.setAlignment(Qt.AlignCenter)
            self.open_camera_btn.setEnabled(True)
            self.close_camera_btn.setEnabled(False)

            # 添加按钮状态变化动画效果
            self.animate_button_state(self.open_camera_btn, True)
            self.animate_button_state(self.close_camera_btn, False)

    def animate_button_state(self, button, enabled):
        """按钮状态变化动画效果"""
        if enabled:
            button.setStyleSheet(button.styleSheet().replace("opacity: 0.5", ""))
        else:
            original_style = button.styleSheet()
            button.setStyleSheet(original_style + "; opacity: 0.5")

    def update_frame(self):
        """更新摄像头画面并处理虚拟键盘"""
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # 手部检测和虚拟键盘处理
                frame = self.detector.findHands(frame)
                lmList, _ = self.detector.findPosition(frame)

                # 翻转图像（镜像效果）
                frame = cv2.flip(frame, 1)

                # 绘制虚拟键盘
                frame = self.draw_all(frame, self.button_list)

                # 检测手指位置并处理点击
                if lmList:
                    for button in self.button_list:
                        x, y = button.pos
                        w, h = button.size

                        # 检查食指是否在按钮上
                        if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                            cv2.rectangle(frame, (x - 5, y - 5), (x + w + 5, y + h + 5),
                                          (175, 0, 175), cv2.FILLED)
                            cv2.putText(frame, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                            # 检测点击（食指和中指的距离）
                            length, _, _ = self.detector.findDistance(8, 12, frame, draw=False)

                            # 如果检测到点击动作
                            if length < 25:
                                cv2.rectangle(frame, button.pos, (x + w, y + h),
                                              (0, 255, 0), cv2.FILLED)
                                cv2.putText(frame, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                                # 更新文本框内容
                                self.final_text += button.text
                                self.text_edit.setText(self.final_text)
                                sleep(0.2)  # 防止重复点击

                # 转换为Qt可显示的格式并更新UI
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                qt_image = convert_to_Qt_format.scaled(self.camera_label.width(), self.camera_label.height(),
                                                       Qt.KeepAspectRatio)
                self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def draw_all(self, img, button_list):
        """绘制所有虚拟按键"""
        for button in button_list:
            x, y = button.pos
            w, h = button.size
            self.corner_rect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]), 20, rt=0)
            cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img

    def corner_rect(self, img, bbox, l=30, t=5, rt=1, colorR=(255, 0, 255), colorC=(0, 255, 0)):
        """绘制带有边角装饰的矩形"""
        x, y, w, h = bbox
        x1, y1 = x + w, y + h
        if rt != 0:
            cv2.rectangle(img, bbox, colorR, rt)
        # 左上角
        cv2.line(img, (x, y), (x + l, y), colorC, t)
        cv2.line(img, (x, y), (x, y + l), colorC, t)
        # 右上角
        cv2.line(img, (x1, y), (x1 - l, y), colorC, t)
        cv2.line(img, (x1, y), (x1, y + l), colorC, t)
        # 左下角
        cv2.line(img, (x, y1), (x + l, y1), colorC, t)
        cv2.line(img, (x, y1), (x, y1 - l), colorC, t)
        # 右下角
        cv2.line(img, (x1, y1), (x1 - l, y1), colorC, t)
        cv2.line(img, (x1, y1), (x1, y1 - l), colorC, t)
        return img

    def clear_text(self):
        """清空文本内容"""
        self.final_text = ""
        self.text_edit.clear()

        # 添加清空文本的动画效果
        palette = self.text_edit.palette()
        palette.setColor(QPalette.Base, QColor(255, 240, 240))
        self.text_edit.setPalette(palette)

        # 恢复背景色
        QTimer.singleShot(500, lambda: self.reset_text_background())

    def reset_text_background(self):
        """恢复文本框背景色"""
        palette = self.text_edit.palette()
        palette.setColor(QPalette.Base, QColor(248, 250, 252))
        self.text_edit.setPalette(palette)

    def save_text(self):
        """保存文本内容到文件"""
        if not self.text_edit.toPlainText():
            QMessageBox.warning(self, "警告", "没有内容可保存!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文本", "", "文本文件 (*.txt);;所有文件 (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "成功", f"文本已保存至 {file_path}")

                # 添加保存成功的视觉反馈
                self.save_text_btn.setStyleSheet(self.save_text_btn.styleSheet() + "; background-color: #4ade80;")
                QTimer.singleShot(1000, lambda: self.reset_save_button_color())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件时出错: {str(e)}")

    def reset_save_button_color(self):
        """恢复保存按钮颜色"""
        self.save_text_btn.setStyleSheet("background-color: #8b5cf6;")

    def close_application(self):
        """关闭应用程序"""
        reply = QMessageBox.question(
            self, '确认退出', '确定要退出程序吗?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.cap is not None:
                self.cap.release()
            self.close()

    def closeEvent(self, event):
        """重写关闭事件，确保资源被正确释放"""
        if self.cap is not None:
            self.cap.release()
        event.accept()


class Button:
    """虚拟按钮类"""

    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualKeyboardGUI()
    window.show()
    sys.exit(app.exec_())
