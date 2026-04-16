# HandPose 手势识别项目

一个基于 OpenCV + MediaPipe 的手势交互项目集合，包含手势识别、虚拟鼠标、虚拟键盘、音量控制、虚拟画板、贪吃蛇和击球小游戏，并提供了 PyQt5 图形化展示入口。

## 项目亮点

- 实时手部关键点检测与手势识别
- 非接触式控制：鼠标、键盘、系统音量
- 手势交互小游戏：贪吃蛇、击球游戏
- 虚拟画板：支持颜色切换与保存绘图
- 提供 GUI 统一入口，便于演示和体验

## 技术栈

- Python
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)
- PyQt5 (`PyQt5`)
- `autopy`（鼠标控制）
- `pynput`（虚拟键盘输入）
- `pycaw` + `comtypes`（Windows 音量控制）
- `cvzone`（拖拽图片模块）

## 目录结构

```text
HandPose/
├─ Basics.py
├─ HandTrackingModule.py
├─ ProjectExample.py
├─ GUI/
│  ├─ mainWindow.py                # GUI 总入口
│  ├─ UiForHandGesture.py
│  ├─ UiForKeyboard.py
│  ├─ UiForMouse.py
│  ├─ UiForPainter.py
│  ├─ UiForVolume.py
│  └─ resources/
├─ Finger/
│  ├─ GestureRecognitionModule.py
│  └─ HandTrackingModule.py
├─ Mouse/
│  ├─ main.py
│  └─ Track.py
├─ KeyBoard/
│  ├─ main.py
│  └─ Track.py
├─ Volume/
│  ├─ VolumeHandControl.py
│  └─ TrackingForVolume.py
├─ VirtualPainter/
│  ├─ VirtualPainter.py
│  ├─ TrackingForPainter.py
│  └─ PainterImg/
├─ Snake/
│  ├─ snake.py
│  └─ track.py
├─ basketballGame/
│  ├─ main.py
│  ├─ handDectector.py
│  └─ Resources/
└─ DragPicture/
   ├─ Drag.py
   ├─ TrackForDrag.py
   └─ ImagesPNG/
```

## 环境准备

> 建议 Python 版本：`3.9 ~ 3.11`（Windows）

1. 创建并激活虚拟环境（可选但推荐）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 安装依赖

```powershell
pip install -r requirements.txt
```

或直接安装：

```powershell
pip install opencv-python mediapipe numpy PyQt5 autopy pynput pycaw comtypes cvzone
```

## 快速开始（推荐）

### 方式 1：GUI 统一入口

从 `GUI` 目录启动：

```powershell
cd GUI
python mainWindow.py
```

说明：
- GUI 首页可进入各功能模块。
- `mainWindow.py` 内部通过子进程启动不同脚本。

### 方式 2：单模块运行

请先 `cd` 到对应模块目录再运行（很多脚本依赖相对路径或同级导入）。

#### 手势识别（基础）

```powershell
python Basics.py
```

#### 手势识别（示例）

```powershell
python ProjectExample.py
```

#### 虚拟鼠标

```powershell
cd Mouse
python main.py
```

#### 虚拟键盘

```powershell
cd KeyBoard
python main.py
```

#### 音量控制（Windows）

```powershell
cd Volume
python VolumeHandControl.py
```

#### 虚拟画板

```powershell
cd VirtualPainter
python VirtualPainter.py
```

#### 手势贪吃蛇

```powershell
cd Snake
python snake.py
```

#### 击球游戏

```powershell
cd basketballGame
python main.py
```

#### 拖拽图片

```powershell
cd DragPicture
python Drag.py
```

## 交互说明（简要）

- 大多数模块默认使用摄像头 `0`。
- 通常按 `Esc` 退出窗口。
- 个别模块支持额外快捷键：
  - 贪吃蛇：`r` 重开
  - 画板：`s` 保存绘图

## 常见问题

### 1. 摄像头打不开

- 确认没有被其他软件占用（腾讯会议、微信、浏览器等）。
- 尝试修改代码中的摄像头索引：`cv2.VideoCapture(0)` 改为 `1`。

### 2. `ModuleNotFoundError`

- 确认已安装依赖。
- 确认在正确目录运行（例如 `Volume`、`Snake`、`basketballGame` 等目录）。

### 3. 音量控制无效

- `pycaw` 仅支持 Windows 系统音频接口。
- 需要正常的扬声器输出设备。

### 4. 运行卡顿

- 降低摄像头分辨率。
- 关闭其它占用 GPU/CPU 的程序。