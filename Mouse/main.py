import cv2
import numpy as np
from Track import handDetector
import time
import autopy

##########################
wCam, hCam = 1080, 680
frameR = 160  # Frame Reduction
smoothening = 7
##########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = handDetector(maxHands=1)
# 获取屏幕尺寸
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)

while True:
    # 获取手部关键点坐标
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 获取食指和中指的指尖坐标
    if len(lmList) != 0:
        # 代表食指和中指的指尖坐标
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

    # 判断手指伸展状态
    fingers = detector.fingersUp()
    # print(fingers)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)
    # 4. 只有食指伸展，移动模式
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 平滑值
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # 移动鼠标
        autopy.mouse.move(wScr - clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY

    # 点击模式
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
        # 指尖距离计算
        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(length)
        # 点击操作
        if length < 20:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()
    # 右键模式
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
        autopy.mouse.click(button=autopy.mouse.Button.RIGHT, delay=0)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    img = cv2.flip(img, 1) 
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
