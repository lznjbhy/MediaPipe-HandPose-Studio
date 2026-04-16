import math
import random
import cv2
import numpy as np
from track import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)


# 将前景图像的非透明区域叠加到背景指定位置，透明区域保持背景可见
def overlayPNG(imgBack, imgFront, pos=[0, 0]):
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape
    *_, mask = cv2.split(imgFront)  # 分离通道，提取Alpha通道（mask），mask是一个单通道灰度图,表示透明度
    maskBGRA = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)  # 将Alpha通道转换为4通道BGRA格式，用于后续位运算
    maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # 将Alpha通道转换为3通道BGR格式，用于生成反色掩码
    imgRGBA = cv2.bitwise_and(imgFront, maskBGRA)  # 前景图像与Alpha掩码按位与，透明区域变为黑色（BGR = 0, A = 0）
    imgRGB = cv2.cvtColor(imgRGBA, cv2.COLOR_BGRA2BGR)  # 转换为3通道BGR图像，丢弃Alpha通道

    # 全黑背景（与imgBack同尺寸）
    imgMaskFull = np.zeros((hb, wb, cb), np.uint8)
    # 将前景放入指定位置
    imgMaskFull[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = imgRGB
    # 全白背景
    imgMaskFull2 = np.ones((hb, wb, cb), np.uint8) * 255
    # 反色掩码（透明区域变白，不透明变黑）
    maskBGRInv = cv2.bitwise_not(maskBGR)
    # 将反色掩码放入指定位置
    imgMaskFull2[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = maskBGRInv
    # 在背景上挖出前景区域（黑色）
    imgBack = cv2.bitwise_and(imgBack, imgMaskFull2)
    # 将前景填充到挖出的区域
    imgBack = cv2.bitwise_or(imgBack, imgMaskFull)

    return imgBack

# 在屏幕上突出显示文本信息
def putTextRect(img, text, pos, scale=3, thickness=3, colorT=(255, 255, 255),
                colorR=(255, 0, 255), font=cv2.FONT_HERSHEY_PLAIN,
                offset=10, border=None, colorB=(0, 255, 0)):
    ox, oy = pos
    (w, h), _ = cv2.getTextSize(text, font, scale, thickness)

    x1, y1, x2, y2 = ox - offset, oy + offset, ox + w + offset, oy - h - offset

    cv2.rectangle(img, (x1, y1), (x2, y2), colorR, cv2.FILLED)
    if border is not None:
        cv2.rectangle(img, (x1, y1), (x2, y2), colorB, border)
    cv2.putText(img, text, (ox, oy), font, scale, colorT, thickness)

    return img, [x1, y2, x2, y1]


class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # 蛇身的所有点
        self.lengths = []  # 每个点之间的距离
        self.currentLength = 0  # 蛇的总长度
        self.allowedLength = 150  # 允许最大长度
        self.previousHead = 0, 0  # 前头部

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 400)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            putTextRect(imgMain, "Game Over", [300, 400],
                        scale=7, thickness=5, offset=20)
            putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                        scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # 长度限制，从尾部开始削减
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # 检查是否吃到了食物
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # 绘制蛇身
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)

            # 绘制食物
            imgMain = overlayPNG(imgMain, self.imgFood,
                                 (rx - self.wFood // 2, ry - self.hFood // 2))

            putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                        scale=3, thickness=3, offset=10)

            # 检测碰撞
            # 排除蛇头和相邻节点（避免误判）
            pts = np.array(self.points[:-2], np.int32)
            # 重塑为OpenCV所需格式 [N,1,2]
            pts = pts.reshape((-1, 1, 2))
            # print(pts)
            # 不闭合多边形
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            # 计算蛇头坐标(cx, cy)到蛇身多边形（pts）的最小距离。
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -2 <= minDist <= 2:
                print("Hit")
                self.gameOver = True
                self.points = []
                self.lengths = []
                self.currentLength = 0
                self.allowedLength = 150
                self.previousHead = 0, 0
                self.randomFoodLocation()

        return imgMain


# Ui界面
game = SnakeGameClass("../GUI/resources/Donut.png")

# 单独运行
# game = SnakeGameClass("Donut.png")

# 重设窗口大小，适应主页面布局大小
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1260, 722)
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 135, 22)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
    if key == 27:  # 按Esc键退出
        break
