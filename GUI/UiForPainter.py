import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QMessageBox, QFrame,
                             QFileDialog, QSplitter, QStatusBar)
from PyQt5.QtGui import (QImage, QPixmap, QPainter, QColor, QPen,
                         QFont, QPalette, QBrush, QLinearGradient, QIcon)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
import os
import VirtualPainter.TrackingForPainter as tcp

# 确保中文显示正常
QApplication.setFont(QFont("SimHei", 9))


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, np.ndarray)
    error_signal = pyqtSignal(str)  # 添加错误信号

    def __init__(self, brush_images_path="D:\me\Graduate\HandPose\VirtualPainter\PainterImg"):
        super().__init__()
        self._run_flag = True
        try:
            # 尝试导入和初始化检测器
            import VirtualPainter.TrackingForPainter as tcp
            self.detector = tcp.handDetector()
        except Exception as e:
            print(f"手部检测器初始化错误: {e}")
            self.error_signal.emit(f"手部检测器初始化错误: {e}")
            raise

        self.color = (255, 0, 0)  # 初始颜色为蓝色
        self.brush_thickness = 15
        self.eraser_thickness = 40
        self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)
        self.xp, self.yp = 0, 0
        self.is_drawing = False

        # 加载画笔选择图片
        self.brush_images = self.load_brush_images(brush_images_path)
        self.current_brush_index = 0

    def load_brush_images(self, path):
        """加载画笔选择区域的图片"""
        images = []
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)]
        try:
            for i in range(1, 5):  # 加载1.png到4.png
                img_path = os.path.join(path, f"{i}.png")
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    if img is not None:
                        # 调整图片大小以适应显示区域
                        img = cv2.resize(img, (320, 100))
                        images.append(img)
                    else:
                        print(f"无法加载图片: {img_path}")
                        # 使用默认颜色创建图像
                        img = np.ones((100, 320, 3), dtype=np.uint8) * np.array(colors[i - 1], dtype=np.uint8)
                        images.append(img)
                else:
                    print(f"图片不存在: {img_path}")
                    # 使用默认颜色创建图像
                    img = np.ones((100, 320, 3), dtype=np.uint8) * np.array(colors[i - 1], dtype=np.uint8)
                    images.append(img)

            return images
        except Exception as e:
            print(f"加载画笔图片时出错: {e}")
            # 创建默认颜色图像
            colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)]
            default_images = []
            for color in colors:
                img = np.ones((100, 320, 3), dtype=np.uint8) * np.array(color, dtype=np.uint8)
                default_images.append(img)
            return default_images

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            cap.set(3, 1280)
            cap.set(4, 720)

            while self._run_flag:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        error_msg = "无法获取摄像头画面。摄像头可能已断开连接。"
                        print(error_msg)
                        self.error_signal.emit(error_msg)
                        break

                    # 镜像翻转
                    frame = cv2.flip(frame, 1)

                    # 手部检测和绘图逻辑
                    try:
                        frame = self.detector.findHands(frame)
                        lmList = self.detector.findPosition(frame, draw=False)
                    except Exception as det_error:
                        print(f"手部检测错误: {det_error}")
                        # 继续处理帧，但不进行手部检测
                        lmList = []

                    # 将当前选择的画笔图像添加到摄像头画面顶部
                    top_image = np.zeros((100, 1280, 3), dtype=np.uint8)
                    resized_brush = cv2.resize(self.brush_images[self.current_brush_index], (1280, 100))
                    top_image[:, :] = resized_brush
                    frame[0:100, :] = top_image

                    if len(lmList) != 0:
                        x1, y1 = lmList[8][1:]  # 食指指尖坐标
                        x2, y2 = lmList[12][1:]  # 中指指尖坐标

                        # 检查手指状态
                        fingers = self.detector.fingersUp()

                        # 选择模式：两指向上
                        if fingers[1] and fingers[2]:
                            self.is_drawing = False
                            # 检测是否在画笔选择区域
                            if y1 < 100:
                                brush_index = x1 // 320  # 确定选择的画笔索引
                                if 0 <= brush_index < len(self.brush_images):
                                    self.current_brush_index = brush_index
                                    # 根据索引设置画笔颜色
                                    self.color = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0)][brush_index]

                        # 绘制模式：只有食指向上
                        if fingers[1] and not fingers[2]:
                            self.is_drawing = True
                            cv2.circle(frame, (x1, y1), 15, self.color, -1)

                            if self.xp == 0 and self.yp == 0:
                                self.xp, self.yp = x1, y1

                            # 绘制线条
                            thickness = self.eraser_thickness if self.color == (0, 0, 0) else self.brush_thickness
                            cv2.line(frame, (self.xp, self.yp), (x1, y1), self.color, thickness)
                            cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.color, thickness)

                            self.xp, self.yp = x1, y1
                        else:
                            self.xp, self.yp = 0, 0

                    # 发送信号更新UI
                    self.change_pixmap_signal.emit(frame, self.imgCanvas)

                    # 控制帧率
                    cv2.waitKey(30)

                except Exception as frame_error:
                    error_msg = f"处理摄像头帧时发生错误: {frame_error}"
                    print(error_msg)
                    self.error_signal.emit(error_msg)
                    break

        except Exception as main_error:
            error_msg = f"视频线程发生严重错误: {main_error}"
            print(error_msg)
            self.error_signal.emit(error_msg)

        finally:
            # 确保摄像头被释放
            if 'cap' in locals():
                cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

    def clear_canvas(self):
        """清除画布"""
        self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)


class HandTrackingPainterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能手势绘图系统")
        self.setGeometry(180, 65, 1570, 905)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cccccc;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QStatusBar {
                background-color: #e9e9e9;
                color: #333333;
                border-top: 1px solid #cccccc;
            }
        """)

        # 创建中心部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 创建顶部标题栏
        self.title_frame = QFrame()
        self.title_frame.setStyleSheet("""
            background-color: #4a86e8;
            border : none
        """)
        self.title_layout = QHBoxLayout(self.title_frame)
        self.title_label = QLabel("智能手势绘图系统")
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 30px;
            font-weight: bold;
            padding: 20px;
        """)
        self.title_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.title_frame)

        # 创建内容区域（左右分栏）
        self.content_splitter = QSplitter(Qt.Horizontal)

        # 左侧：摄像头显示区域
        self.camera_frame = QFrame()
        self.camera_layout = QVBoxLayout(self.camera_frame)

        self.camera_title = QLabel("摄像头画面")
        self.camera_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            padding: 8px;
        """)
        self.camera_layout.addWidget(self.camera_title, alignment=Qt.AlignCenter)

        self.camera_display = QLabel("点击下方按钮开启摄像头")
        self.camera_display.setAlignment(Qt.AlignCenter)
        self.camera_display.setMinimumSize(640, 480)
        self.camera_display.setStyleSheet("""
            background-color: #e9e9e9;
            border-radius: 4px;
        """)
        self.camera_layout.addWidget(self.camera_display, alignment=Qt.AlignCenter)

        self.content_splitter.addWidget(self.camera_frame)

        # 右侧：绘图结果显示区域
        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout(self.result_frame)

        self.result_title = QLabel("绘图结果")
        self.result_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            padding: 8px;
        """)
        self.result_layout.addWidget(self.result_title, alignment=Qt.AlignCenter)

        self.result_display = QLabel("绘图内容将显示在这里")
        self.result_display.setAlignment(Qt.AlignCenter)
        self.result_display.setMinimumSize(640, 480)
        self.result_display.setStyleSheet("""
            background-color: #e9e9e9;
            border-radius: 4px;
        """)
        self.result_layout.addWidget(self.result_display, alignment=Qt.AlignCenter)

        self.content_splitter.addWidget(self.result_frame)

        # 设置分割器比例
        self.content_splitter.setSizes([600, 600])
        self.main_layout.addWidget(self.content_splitter, 4)

        # 创建底部按钮区域
        self.bottom_frame = QFrame()
        self.bottom_layout = QHBoxLayout(self.bottom_frame)

        self.start_btn = QPushButton("开启摄像头")
        self.start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setFont(QFont("SimHei", 12))
        self.start_btn.clicked.connect(self.start_camera)
        self.bottom_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("关闭摄像头")
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFont(QFont("SimHei", 12))
        self.bottom_layout.addWidget(self.stop_btn)

        self.save_btn = QPushButton("保存作品")
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setFont(QFont("SimHei", 12))
        self.save_btn.setEnabled(False)
        self.bottom_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("清除画布")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_canvas)
        self.clear_btn.setEnabled(False)
        self.bottom_layout.addWidget(self.clear_btn)

        self.exit_btn = QPushButton("退出系统")
        self.exit_btn.setIcon(QIcon.fromTheme("application-exit"))
        self.exit_btn.setMinimumHeight(40)
        self.exit_btn.clicked.connect(self.close)
        self.bottom_layout.addWidget(self.exit_btn)

        self.main_layout.addWidget(self.bottom_frame, 1)

        # 创建状态栏
        self.statusBar().showMessage("就绪")

        # 初始化视频线程
        self.thread = None

    def start_camera(self):
        # 获取画笔图片路径
        brush_images_path = "D:\me\Graduate\HandPose\VirtualPainter\PainterImg"  # 请替换为实际路径

        try:
            # 创建并启动视频线程
            self.thread = VideoThread(brush_images_path)

            # 连接信号
            self.thread.change_pixmap_signal.connect(self.update_frames)

            # 添加错误处理信号
            self.thread.error_signal.connect(self.handle_camera_error)

            # 启动线程
            self.thread.start()

            # 更新按钮状态
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            self.statusBar().showMessage("摄像头已开启，开始绘图吧！")

        except Exception as e:
            # 处理线程创建或启动失败的情况
            error_msg = f"启动摄像头失败: {e}"
            QMessageBox.critical(self, "错误", error_msg)
            self.statusBar().showMessage(error_msg)
            self.thread = None

    def handle_camera_error(self, error_msg):
        """处理摄像头线程中的错误"""
        # 停止摄像头
        self.stop_camera()

        # 显示错误消息
        QMessageBox.critical(self, "摄像头错误", error_msg)

        # 更新状态栏
        self.statusBar().showMessage("摄像头发生错误，已自动关闭")

    def stop_camera(self):
        # 停止视频线程
        if self.thread is not None:
            self.thread.stop()
            self.thread = None

        # 更新按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.statusBar().showMessage("摄像头已关闭")

        # 重置显示
        self.camera_display.setText("点击下方按钮开启摄像头")
        self.result_display.setText("绘图内容将显示在这里")

    def update_frames(self, camera_frame, result_frame):
        """更新摄像头画面和绘图结果显示"""
        # 更新摄像头画面
        if camera_frame is not None:
            self.display_image(self.camera_display, camera_frame)

        # 更新绘图结果画面
        if result_frame is not None and np.sum(result_frame) > 0:
            self.display_image(self.result_display, result_frame)
        else:
            self.result_display.setText("绘图内容将显示在这里")

    def display_image(self, label, cv_img):
        """将OpenCV图像显示在QLabel上"""
        if cv_img is None:
            return

        # 确保图像格式正确
        if len(cv_img.shape) == 2:  # 灰度图像
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
        else:  # BGR彩色图像
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        # 创建QImage对象
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # 缩放图像以适应QLabel大小，同时保持比例
        scaled_img = q_img.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 在QLabel上显示图像
        label.setPixmap(QPixmap.fromImage(scaled_img))

    def save_image(self):
        if self.thread is not None:
            try:
                # 获取当前绘图结果
                result_image = self.thread.imgCanvas

                if np.sum(result_image) == 0:
                    QMessageBox.warning(self, "警告", "画布为空，无需保存")
                    return

                # 打开文件对话框选择保存位置
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "保存图片", os.path.expanduser("~"), "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*)"
                )

                if file_path:
                    # 保存图片
                    cv2.imwrite(file_path, result_image)

                    # 显示保存成功消息
                    QMessageBox.information(self, "保存成功", f"图片已成功保存到:\n{file_path}")
                    self.statusBar().showMessage(f"图片已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存图片时出错: {str(e)}")
                self.statusBar().showMessage("保存图片失败")
        else:
            QMessageBox.warning(self, "警告", "请先开启摄像头进行绘图")

    def clear_canvas(self):
        if self.thread is not None:
            self.thread.clear_canvas()
            self.result_display.setText("绘图内容将显示在这里")
            self.statusBar().showMessage("画布已清空")

    def closeEvent(self, event):
        # 确保线程在关闭应用时停止
        if self.thread is not None:
            self.thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandTrackingPainterApp()
    window.show()
    sys.exit(app.exec_())