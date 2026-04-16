import cv2
import TrackingForPainter as tcp
import os
import numpy as np

folderPath = "PainterImg/"
mylist = os.listdir(folderPath)
overlayList = []
for imPath in mylist:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
# 默认颜色
header = overlayList[0]
color = [255, 0, 0]
brushThickness = 15
eraserThickness = 40

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = tcp.handDetector()
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)  # 新建一个纯黑色画板

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1240, 775)
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # 手指竖起状态
        fingers = detector.fingersUp()

        # 双指竖立，为选择模式
        if fingers[1] and fingers[2]:
            if y1 < 153:
                if 0 < x1 < 320:
                    header = overlayList[0]
                    color = [255, 0, 0]
                elif 320 < x1 < 640:
                    header = overlayList[1]
                    color = [0, 0, 255]
                elif 640 < x1 < 960:
                    header = overlayList[2]
                    color = [0, 255, 0]
                elif 960 < x1 < 1280:
                    header = overlayList[3]
                    color = [0, 0, 0]
        img[0:1280][0:153] = header

        # 食指控制画笔移动
        if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1, y1), 15, color, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if color == [0, 0, 0]:
                cv2.line(img, (xp, yp), (x1, y1), color, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), color, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, brushThickness)

        xp, yp = x1, y1

    # 实时显示画笔轨迹的实现
    # 转为灰度图
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    # 反二值化，大于50(有画笔)->0（黑色）,小于50（无画笔）->255（白色）
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)
    img[0:1280][0:153] = header

    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 135, 22)
    key = cv2.waitKey(1)
    if key == 27:  # 按Esc键退出
        break
    elif key == ord('s'):  # 按's'键保存图片
        cv2.imwrite('drawn_image.png', imgCanvas)
        print("Image saved successfully!")

cap.release()
cv2.destroyAllWindows()
