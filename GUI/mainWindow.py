import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGridLayout, QStackedWidget, QFrame)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QPoint


class ProjectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('项目展示平台')
        self.setGeometry(180, 65, 1570, 780)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QPushButton {
                background-color: #4a89dc;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3b78c7;
            }
            QLabel {
                color: #333;
            }
        """)

        # 创建堆叠小部件用于页面切换
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 创建主页面
        self.main_page = MainPage(self)

        # 项目详细介绍内容
        project_descriptions = [
            """
            手势识别项目基于先进的计算机视觉技术，能够实时准确地识别用户的手部动作和手势。

            主要功能包括：
            - 实时跟踪手部位置和运动轨迹
            - 实时识别不同的手势动作
            - 展示标准的手势图

            通过本项目，您可以体验到基于摄像头实时识别手势动作的乐趣。
            """,
            """
            经典贪吃蛇游戏的手势控制版，融合了流畅的动画效果和简洁的界面设计。

            主要功能包括：
            - 手指控制蛇头的运动
            - 实时统计分数

            重温经典游戏的乐趣，挑战您的反应速度和策略思维！
            """,
            """
            击球游戏是一款基于手部动作的休闲游戏，玩家需要控制球拍击球得分。

            主要功能包括：
            - 真实的物理模拟和碰撞效果
            - 实时计分系统
            - 精美的视觉效果和流畅的动画

            单人就能开玩！享受击球的乐趣，挑战高分，成为击球大师！
            """,
            """
            音量控制项目通过手势实现非接触式音量调节。

            主要功能包括：
            - 手势识别控制音量大小
            - 实时显示当前音量状态
            - 支持静音、增大和减小音量等操作

            无需触摸设备，通过简单的手势即可控制音量，为您带来更加便捷的操作体验。
            """,
            """
            虚拟鼠标项目使用计算机视觉技术，将您的手部动作转换为鼠标操作。

            主要功能包括：
            - 手部跟踪实现光标移动
            - 手势识别实现鼠标点击操作
            - 支持常用的鼠标点击操作

            无需物理鼠标，通过手部动作即可控制计算机，为您提供更加自由的操作方式。
            """,
            """
            虚拟键盘项目基于计算机视觉技术，实现了非接触式的键盘输入。

            主要功能包括：
            - 虚拟键盘界面实时显示
            - 手势识别实现字符输入

            在没有物理键盘的情况下，通过手部动作即可实现文本输入，为您提供更多的输入选择。
            """,
            """
            虚拟画板项目允许用户通过手势在屏幕上进行绘画创作。

            主要功能包括：
            - 多种画笔颜色自由选择
            - 实时绘画预览和清除功能
            - 支持保存作品

            释放您的创造力，通过简单的手势在数字画布上创作出精美的作品。
            """,
        ]

        # 创建7个项目页面，传入不同的介绍内容
        self.project_pages = []
        for i in range(7):
            project_page = ProjectPage(self, f"项目{i + 1}", project_descriptions[i])
            self.project_pages.append(project_page)

        # 将所有页面添加到堆叠小部件，进行页面切换
        self.stacked_widget.addWidget(self.main_page)
        for page in self.project_pages:
            self.stacked_widget.addWidget(page)

        # 设置背景色
        self.set_background_color("#f5f7fa")

    # 使用调色板机制
    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.white)
        self.setPalette(palette)

    def show_project_page(self, project_index):
        # 添加页面切换动画
        current_idx = self.stacked_widget.currentIndex()
        next_idx = project_index + 1  # 主页面索引为0

        self.stacked_widget.setCurrentIndex(next_idx)

        # 页面切换动画
        if current_idx != next_idx:
            animation = QPropertyAnimation(self.stacked_widget, b"pos")
            animation.setDuration(300)
            animation.setStartValue(QPoint(0, 0))
            animation.setEndValue(QPoint(0, 0))
            animation.start()

    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(0)


class MainPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # 创建标题
        title_label = QLabel("精选项目体验")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(title_label)
        # 创建两个独立的网格布局，分别用于两行项目
        # 第一行（三张图片）使用居中布局
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)
        top_layout.setAlignment(Qt.AlignCenter)

        # 第二行（四张图片）使用占满宽度的布局
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(30)
        bottom_layout.setAlignment(Qt.AlignJustify)

        button_texts = ["手势识别", "贪吃蛇", "击球游戏", "音量控制", "虚拟鼠标", "虚拟键盘", "虚拟画板"]
        for i in range(7):
            card = self.create_project_card(i, button_texts[i])
            if i < 3:  # 第一行
                top_layout.addWidget(card)
            else:  # 第二行
                bottom_layout.addWidget(card)

        # 添加两个布局到主布局
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_project_card(self, index, button_text):
        # 创建项目卡片
        card = QWidget()
        card.setFixedSize(320, 340)  # 增加卡片高度以容纳按钮
        card.setObjectName(f"projectCard{index}")
        card.setStyleSheet(f"""
            #projectCard{index} {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }}
            #projectCard{index}:hover {{
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                transform: translateY(-5px);
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # 创建图片展示区域
        image_container = QWidget()
        image_container.setStyleSheet("""
            background-color: #ecf0f1;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)

        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(10, 10, 10, 10)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setScaledContents(True)

        # 保持原图片设置不变
        image_path = f"resources/mainWindow_{index + 1}.png"
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                image_label.setPixmap(pixmap)
            else:
                image_label.setText(f"项目{index + 1}")
                image_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #7f8c8d;")
        except Exception as e:
            print(f"加载图片 {image_path} 时出错: {e}")
            image_label.setText(f"项目{index + 1}")
            image_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #7f8c8d;")

        image_layout.addWidget(image_label)
        card_layout.addWidget(image_container, 4)  # 图片占据4/5空间

        # 创建按钮区域
        button_container = QWidget()
        button_container.setStyleSheet("""
            background-color: white;
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
            padding: 15px;
        """)

        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 使用传入的文本设置按钮内容
        project_button = QPushButton(button_text)
        project_button.setFixedSize(180, 55)  # 增大按钮尺寸
        project_button.setStyleSheet("""
            QPushButton {
                background-color: #4a89dc;
                color: white;
                border-radius: 5px;
                font-size: 18px;
                font-weight: 500;
                margin: 0 auto;
            }
            QPushButton:hover {
                background-color: #3b78c7;
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """)
        project_button.clicked.connect(lambda checked, i=index: self.parent.show_project_page(i))

        button_layout.addWidget(project_button, alignment=Qt.AlignCenter)
        card_layout.addWidget(button_container, 1)  # 按钮占据1/5空间

        return card


class ProjectPage(QWidget):
    def __init__(self, parent, title, description):
        super().__init__()
        self.parent = parent
        self.title = title
        self.description = description
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建顶部导航栏
        nav_bar = QWidget()
        nav_bar.setFixedHeight(60)
        nav_bar.setStyleSheet("""
            background-color: #34495e;
            color: white;
            padding: 0 20px;
        """)

        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        # 返回按钮
        back_button = QPushButton("返回")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 14px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                transform: none;
                box-shadow: none;
            }
        """)
        back_button.setIcon(self.style().standardIcon(self.style().SP_ArrowBack))
        back_button.clicked.connect(self.parent.show_main_page)
        nav_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # 页面标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)
        nav_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # 占位，保持导航栏对称
        spacer = QWidget()
        nav_layout.addWidget(spacer, alignment=Qt.AlignRight)

        layout.addWidget(nav_bar)

        # 内容区域
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #f5f7fa; padding: 40px;")

        content_layout = QVBoxLayout(content_container)

        # 项目标题
        project_title = QLabel(f"项目介绍")
        project_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        content_layout.addWidget(project_title, alignment=Qt.AlignCenter)

        # 项目图片
        project_image = QLabel()
        project_image.setFixedHeight(350)
        project_image.setAlignment(Qt.AlignCenter)
        project_image.setStyleSheet("background-color: #ecf0f1; border-radius: 10px;")

        # 保持原图片设置不变
        image_path = f"resources/mainWindow_{self.title[-1]}.png"
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    800, 350,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                project_image.setPixmap(scaled_pixmap)
            else:
                project_image.setText(f"{self.title}展示图")
                project_image.setStyleSheet("""
                    background-color: #ecf0f1; 
                    border-radius: 10px;
                    font-size: 24px;
                    color: #7f8c8d;
                """)
        except Exception as e:
            print(f"加载项目图片 {image_path} 时出错: {e}")
            project_image.setText(f"{self.title}展示图")
            project_image.setStyleSheet("""
                background-color: #ecf0f1; 
                border-radius: 10px;
                font-size: 24px;
                color: #7f8c8d;
            """)

        content_layout.addWidget(project_image, alignment=Qt.AlignCenter)

        # 项目描述 - 使用传入的详细描述
        project_desc = QLabel(self.description)
        project_desc.setWordWrap(True)
        project_desc.setStyleSheet("""
            font-size: 16px;
            color: #333;
            margin-top: 30px;
            line-height: 1.8;
            padding: 0 100px;
        """)
        content_layout.addWidget(project_desc)

        # 功能按钮
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # 演示按钮
        demo_button = QPushButton("开始演示")
        demo_button.setFixedSize(180, 45)
        demo_button.setStyleSheet("""
            QPushButton {
                background-color: #4a89dc;
                color: white;
                border-radius: 5px;
                font-size: 18px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3b78c7;
            }
        """)
        # 将按钮的点击信号连接到 run_external_script 方法，并传递当前项目的标题
        demo_button.clicked.connect(lambda: self.run_external_script(self.title))

        buttons_layout.addWidget(demo_button)

        content_layout.addWidget(buttons_container, alignment=Qt.AlignCenter)
        content_layout.addStretch()

        layout.addWidget(content_container)
        self.setLayout(layout)

    def run_external_script(self, title):
        script_mapping = {
            "项目1": "UiForHandGesture.py",
            "项目2": "../Snake/snake.py",
            "项目3": "../basketballGame/main.py",
            "项目4": "UiForVolume.py",
            "项目5": "UiForMouse.py",
            "项目6": "UiForKeyboard.py",
            "项目7": "UiForPainter.py"
        }
        subprocess.Popen([sys.executable, script_mapping[title]])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 尝试设置高DPI显示
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = ProjectApp()
    window.show()
    sys.exit(app.exec_())
