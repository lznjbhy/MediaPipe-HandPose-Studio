import autopy
import cv2
from Track import HandDetector
from time import sleep
import numpy as np
from pynput.keyboard import Controller

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""

keyboard = Controller()
wScr, hScr = autopy.screen.size()

# 绘制键盘边框
def cornerRect(img, bbox, l=30, t=5, rt=1,
               colorR=(255, 0, 255), colorC=(0, 255, 0)):
    """
    img：输入的图像（numpy 数组）
    bbox：边界框坐标
    l：角线的长度（默认30像素）
    t：线条的粗细（默认5像素）
    rt：矩形边框的粗细（默认1像素，0表示不绘制矩形）
    colorR：键盘内容颜色（默认紫色）
    colorC：角线的颜色（默认绿色）
    """
    x, y, w, h = bbox
    x1, y1 = x + w, y + h
    if rt != 0:
        cv2.rectangle(img, bbox, colorR, rt)
    # 左上角 L形线条
    cv2.line(img, (x, y), (x + l, y), colorC, t)
    cv2.line(img, (x, y), (x, y + l), colorC, t)
    # 右上角 L形线条
    cv2.line(img, (x1, y), (x1 - l, y), colorC, t)
    cv2.line(img, (x1, y), (x1, y + l), colorC, t)
    # Bottom Left  x,y1
    cv2.line(img, (x, y1), (x + l, y1), colorC, t)
    cv2.line(img, (x, y1), (x, y1 - l), colorC, t)
    # 右下角 L形线条
    cv2.line(img, (x1, y1), (x1 - l, y1), colorC, t)
    cv2.line(img, (x1, y1), (x1, y1 - l), colorC, t)
    return img


def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                   20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img


class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


# print(len(keys))
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1240, 775)
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, _ = detector.findPosition(img)
    # img = cv2.flip(img, 1)
    img = drawAll(img, buttonList)
    # print(lmList)
    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(l)

                # 达到距离阈值，触发点击操作
                if l < 25:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text
                    sleep(0.3)

    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 135, 22)
    key = cv2.waitKey(1)
    if key == 27:  # 按Esc键退出
        break
