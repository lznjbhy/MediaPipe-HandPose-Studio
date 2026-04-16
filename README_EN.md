# HandPose Gesture Interaction Project

A hand gesture interaction project suite built with OpenCV + MediaPipe. It includes gesture recognition, virtual mouse, virtual keyboard, system volume control, virtual painter, snake game, and a paddle-ball game, with a PyQt5 GUI entry for easier demos.

## Highlights

- Real-time hand landmark detection and gesture recognition
- Touchless control: mouse, keyboard, and system volume
- Gesture-driven mini games: Snake and Paddle Ball
- Virtual painter with color switching and canvas saving
- Unified GUI launcher for quick demonstration

## Tech Stack

- Python
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)
- PyQt5 (`PyQt5`)
- `autopy` (mouse control)
- `pynput` (virtual keyboard input)
- `pycaw` + `comtypes` (Windows volume control)
- `cvzone` (image dragging module)

## Project Structure

```text
HandPose/
├─ Basics.py
├─ HandTrackingModule.py
├─ ProjectExample.py
├─ GUI/
│  ├─ mainWindow.py                # Main GUI entry
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

## Environment Setup

> Recommended Python version: `3.9 ~ 3.11` (Windows)

1. Create and activate a virtual environment (optional but recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

Or install directly:

```powershell
pip install opencv-python mediapipe numpy PyQt5 autopy pynput pycaw comtypes cvzone
```

## Quick Start (Recommended)

### Option 1: Unified GUI Launcher

Run from the `GUI` folder:

```powershell
cd GUI
python mainWindow.py
```

Notes:
- Use the home screen to enter each module.
- `mainWindow.py` launches module scripts via subprocess.

### Option 2: Run Individual Modules

Please `cd` into each module folder before running scripts, since many scripts rely on relative paths or local imports.

#### Basic Gesture Recognition

```powershell
python Basics.py
```

#### Gesture Recognition Demo

```powershell
python ProjectExample.py
```

#### Virtual Mouse

```powershell
cd Mouse
python main.py
```

#### Virtual Keyboard

```powershell
cd KeyBoard
python main.py
```

#### Volume Control (Windows)

```powershell
cd Volume
python VolumeHandControl.py
```

#### Virtual Painter

```powershell
cd VirtualPainter
python VirtualPainter.py
```

#### Gesture Snake

```powershell
cd Snake
python snake.py
```

#### Paddle Ball Game

```powershell
cd basketballGame
python main.py
```

#### Drag Picture Demo

```powershell
cd DragPicture
python Drag.py
```

## Interaction Notes

- Most modules use camera index `0` by default.
- Press `Esc` to exit in most windows.
- Extra shortcuts in specific modules:
  - Snake: `r` to restart
  - Painter: `s` to save drawing

## FAQ

### 1. Camera cannot be opened

- Make sure no other app is using the camera.
- Try changing camera index in code from `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`.

### 2. `ModuleNotFoundError`

- Ensure dependencies are installed.
- Ensure you are running scripts from the correct folder (for example `Volume`, `Snake`, `basketballGame`).

### 3. Volume control does not work

- `pycaw` is Windows-only for system audio endpoint control.
- Make sure your output audio device is available.

### 4. Low FPS / lag

- Reduce camera resolution in script settings.
- Close other CPU/GPU intensive applications.

## Possible Improvements

- Add automated dependency lock file and one-click setup scripts
- Add cross-platform volume control alternatives (macOS / Linux)
- Refactor imports and paths into a cleaner package layout
- Add tests and performance benchmarking for each module

## License

No explicit license is included in this repository yet. For open-source release, consider adding a `LICENSE` file (for example MIT).
