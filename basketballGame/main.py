import cv2
from handDectector import HandDetector
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# 单独运行
# imgBackground = cv2.imread("Resources/Background.png")
# imgGameOver = cv2.imread("Resources/gameOver.png")
# imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
# imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
# imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

# Ui界面
imgBackground = cv2.imread("../GUI/resources/Background.png")
imgGameOver = cv2.imread("../GUI/resources/gameOver.png")
imgBall = cv2.imread("../GUI/resources/Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("../GUI/resources/bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("../GUI/resources/bat2.png", cv2.IMREAD_UNCHANGED)

detector = HandDetector(detectionCon=0.8, maxHands=2)

# 初始化参数
ballPos = [100, 100]
speedX = 15
speedY = 15
gameOver = False
score = [0, 0]


def overlayPNG(imgBack, imgFront, pos=[0, 0]):
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape
    *_, mask = cv2.split(imgFront)
    maskBGRA = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
    maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    imgRGBA = cv2.bitwise_and(imgFront, maskBGRA)
    imgRGB = cv2.cvtColor(imgRGBA, cv2.COLOR_BGRA2BGR)

    imgMaskFull = np.zeros((hb, wb, cb), np.uint8)
    imgMaskFull[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = imgRGB
    imgMaskFull2 = np.ones((hb, wb, cb), np.uint8) * 255
    maskBGRInv = cv2.bitwise_not(maskBGR)
    imgMaskFull2[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = maskBGRInv

    imgBack = cv2.bitwise_and(imgBack, imgMaskFull2)
    imgBack = cv2.bitwise_or(imgBack, imgMaskFull)

    return imgBack


cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1260, 722)
while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    # 获取关键点
    hands, img = detector.findHands(img, flipType=False)

    # 覆盖游戏背景图
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    # 检测手部
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            y = y + h // 2
            y1 = y - h1 // 2
            y1 = np.clip(y1, 20, 415)

            if hand['type'] == "Left":
                img = overlayPNG(img, imgBat1, (59, y1))
                if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] += 30
                    score[0] += 1

            if hand['type'] == "Right":
                img = overlayPNG(img, imgBat2, (1195, y1))
                if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] -= 30
                    score[1] += 1

    # 游戏结束
    if ballPos[0] < 40 or ballPos[0] > 1200:
        gameOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
                    2.5, (200, 0, 200), 5)

    else:

        if ballPos[1] >= 500 or ballPos[1] <= 10:
            speedY = -speedY

        ballPos[0] += speedX
        ballPos[1] += speedY

        # 绘制小球
        img = overlayPNG(img, imgBall, ballPos)

        cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 135, 22)
    key = cv2.waitKey(1)
    if key == ord('r'):
        ballPos = [100, 100]
        speedX = 15
        speedY = 15
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("Resources/gameOver.png")
    if key == 27:  # 按Esc键退出
        break
