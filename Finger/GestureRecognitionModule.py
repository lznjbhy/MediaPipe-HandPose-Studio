# import cv2
# import time
# import math
# import HandTrackingModule as htm
#
# wCam, hCam = 640, 480
#
# cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)
# detector = htm.handDetector()
#
#
# def is_thumb_up(hand_list: list):
#     return hand_list[4][1] > hand_list[2][1]
#
#
# def is_index_up(hand_list: list):
#     return hand_list[8][2] < hand_list[6][2]
#
#
# def is_middle_up(hand_list: list):
#     return hand_list[12][2] < hand_list[10][2]
#
#
# def is_ring_up(hand_list: list):
#     return hand_list[16][2] < hand_list[10][2]
#
#
# def is_pinky_up(hand_list: list):
#     return hand_list[20][2] < hand_list[18][2]
#
#
# def is_one(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_down = not is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#
#     return thumb_down and index_up and middle_down and ring_down and pinky_down
#
#
# def is_two(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_up = is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#
#     return thumb_down and index_up and middle_up and ring_down and pinky_down
#
#
# def is_three(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_up = is_middle_up(hand_list)
#     ring_up = is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#     return thumb_down and index_up and middle_up and ring_up and pinky_down
#
#
# def is_four(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_up = is_middle_up(hand_list)
#     ring_up = is_ring_up(hand_list)
#     pinky_up = is_pinky_up(hand_list)
#     return thumb_down and index_up and middle_up and ring_up and pinky_up
#
#
# def is_five(hand_list: list):
#     thumb_up = is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_up = is_middle_up(hand_list)
#     ring_up = is_ring_up(hand_list)
#     pinky_up = is_pinky_up(hand_list)
#     return thumb_up and index_up and middle_up and ring_up and pinky_up
#
#
# def is_six(hand_list: list):
#     thumb_up = is_thumb_up(hand_list)
#     index_down = not is_index_up(hand_list)
#     middle_down = not is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_up = is_pinky_up(hand_list)
#     return thumb_up and index_down and middle_down and ring_down and pinky_up
#
#
# def is_seven(hand_list: list):
#     thumb_up = is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_up = is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#     return thumb_up and index_up and middle_up and ring_down and pinky_down
#     # return judge_distance(hand_list) and pinky_up
#
#
# def judge_distance(hand_list: list):
#     tip_list = [hand_list[4], hand_list[8], hand_list[12], hand_list[16], hand_list[20]]
#     n = len(tip_list)
#     print(n)
#     distance = 0
#     count = 0
#     for i in range(n):
#         for j in range(i + 1, n):
#             x1 = tip_list[i][1]
#             x2 = tip_list[j][1]
#             y1 = tip_list[i][2]
#             y2 = tip_list[j][2]
#             distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#             count = count + 1
#     if distance / count < 50:
#         return True
#     return False
#
#
# def is_eight(hand_list: list):
#     thumb_up = is_thumb_up(hand_list)
#     index_up = is_index_up(hand_list)
#     middle_down = not is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#     return thumb_up and index_up and middle_down and ring_down and pinky_down
#
#
# def is_nine(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     if judge_y(hand_list, 7, 6) < 8:
#         index_down = True
#     else:
#         index_down = False
#     middle_down = not is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#     return thumb_down and index_down and middle_down and ring_down and pinky_down
#
#
# def judge_y(hand_list: list, point1, point2):
#     y1 = hand_list[point1][2]
#     y2 = hand_list[point2][2]
#     Deviation_y = abs(y1 - y2)
#     return Deviation_y
#
#
# def cal_distance(hand_list: list, point1, point2):
#     x1 = hand_list[point1][1]
#     y1 = hand_list[point1][2]
#     x2 = hand_list[point2][1]
#     y2 = hand_list[point2][2]
#     distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#     return distance
#
#
# def is_ten(hand_list: list):
#     thumb_down = not is_thumb_up(hand_list)
#     index_down = (not is_index_up(hand_list)) and (judge_y(hand_list, 7, 6) > 8)
#     middle_down = not is_middle_up(hand_list)
#     ring_down = not is_ring_up(hand_list)
#     pinky_down = not is_pinky_up(hand_list)
#     return thumb_down and index_down and middle_down and ring_down and pinky_down
#
#
# def is_ok(hand_list: list):
#     if cal_distance(hand_list, 8, 4) < 25:
#         ok_flag = True
#     else:
#         ok_flag = False
#     middle_up = is_middle_up(hand_list)
#     ring_up = is_ring_up(hand_list)
#     pinky_up = is_pinky_up(hand_list)
#     return ok_flag and middle_up and ring_up and pinky_up
#
#
# def get_gesture(hand_list: list):
#     if is_one(hand_list):
#         return 1
#     elif is_two(hand_list):
#         return 2
#     elif is_three(hand_list):
#         return 3
#     elif is_four(hand_list):
#         return 4
#     elif is_five(hand_list):
#         return 5
#     elif is_six(hand_list):
#         return 6
#     elif is_seven(hand_list):
#         return 7
#     elif is_eight(hand_list):
#         return 8
#     elif is_nine(hand_list):
#         return 9
#     elif is_ten(hand_list):
#         return 10
#     elif is_ok(hand_list):
#         return "ok"
#     else:
#         return "UnKnown"
#
#
# while True:
#     success, img = cap.read()
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img, draw=False)
#     img = cv2.flip(img, 1)
#     if len(lmList) != 0:
#         # print(judge_y(lmList, 7, 6))
#         # is_up = f"{is_thumb_up(lmList)}+{is_middle_up(lmList)}+{is_ring_up(lmList)}+{is_pinky_up(lmList)}"
#         # print(is_up)
#         cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
#         cv2.putText(img, str(get_gesture(lmList)), (45, 375), cv2.FONT_HERSHEY_PLAIN,
#                     10, (255, 0, 0), 25)
#     cv2.imshow("Image", img)
#     cv2.waitKey(1)


# 封装成类，方便ui程序调用
import cv2
import math
import HandTrackingModule as htm


class GestureRecognizer:
    def __init__(self):
        self.detector = htm.handDetector()

    def find_hands(self, img):
        """查找和标记手部"""
        return self.detector.findHands(img)

    def find_position(self, img, draw=False):
        """查找手部位置"""
        return self.detector.findPosition(img, draw=draw)

    def process_image(self, img, print_result=True):
        """处理图像并返回处理后的图像和手势结果"""
        img = self.find_hands(img)
        lmList = self.find_position(img, draw=False)
        img = cv2.flip(img, 1)  # 镜像翻转

        gesture_result = "Unknown"

        if len(lmList) != 0:
            gesture_result = self.get_gesture(lmList)
            if print_result:
                # 绘制手势结果
                cv2.putText(img, str(gesture_result), (330, 80), cv2.FONT_HERSHEY_PLAIN,
                            4, (255, 0, 0), 10)

        return img, gesture_result

    def is_thumb_up(self, hand_list: list):
        return hand_list[4][1] > hand_list[2][1]

    def is_index_up(self, hand_list: list):
        return hand_list[8][2] < hand_list[6][2]

    def is_middle_up(self, hand_list: list):
        return hand_list[12][2] < hand_list[10][2]

    def is_ring_up(self, hand_list: list):
        return hand_list[16][2] < hand_list[14][2]

    def is_pinky_up(self, hand_list: list):
        return hand_list[20][2] < hand_list[18][2]

    def is_one(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_down = not self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)

        return thumb_down and index_up and middle_down and ring_down and pinky_down

    def is_two(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_up = self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)

        return thumb_down and index_up and middle_up and ring_down and pinky_down

    def is_three(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_up = self.is_middle_up(hand_list)
        ring_up = self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)
        return thumb_down and index_up and middle_up and ring_up and pinky_down

    def is_four(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_up = self.is_middle_up(hand_list)
        ring_up = self.is_ring_up(hand_list)
        pinky_up = self.is_pinky_up(hand_list)
        return thumb_down and index_up and middle_up and ring_up and pinky_up

    def is_five(self, hand_list: list):
        thumb_up = self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_up = self.is_middle_up(hand_list)
        ring_up = self.is_ring_up(hand_list)
        pinky_up = self.is_pinky_up(hand_list)
        return thumb_up and index_up and middle_up and ring_up and pinky_up

    def is_six(self, hand_list: list):
        thumb_up = self.is_thumb_up(hand_list)
        index_down = not self.is_index_up(hand_list)
        middle_down = not self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_up = self.is_pinky_up(hand_list)
        return thumb_up and index_down and middle_down and ring_down and pinky_up

    def is_seven(self, hand_list: list):
        thumb_up = self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_up = self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)
        dis_8_12 = self.cal_distance(hand_list, 8, 12)
        dis_4_8 = self.cal_distance(hand_list, 4, 8)
        if dis_8_12 < 35 and dis_4_8 < 50:
            seven_flag = True
        else:
            seven_flag = False
        return thumb_up and index_up and middle_up and ring_down and pinky_down and seven_flag

    def judge_distance(self, hand_list: list):
        tip_list = [hand_list[4], hand_list[8], hand_list[12], hand_list[16], hand_list[20]]
        n = len(tip_list)
        distance = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                x1 = tip_list[i][1]
                x2 = tip_list[j][1]
                y1 = tip_list[i][2]
                y2 = tip_list[j][2]
                distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                count = count + 1
        if distance / count < 50:
            return True
        return False

    def is_eight(self, hand_list: list):
        thumb_up = self.is_thumb_up(hand_list)
        index_up = self.is_index_up(hand_list)
        middle_down = not self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)
        return thumb_up and index_up and middle_down and ring_down and pinky_down

    def judge_y(self, hand_list: list, point1, point2):
        y1 = hand_list[point1][2]
        y2 = hand_list[point2][2]
        Deviation_y = abs(y1 - y2)
        return Deviation_y

    def is_nine(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        if self.judge_y(hand_list, 7, 6) < 8:
            index_down = True
        else:
            index_down = False
        middle_down = not self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)
        return thumb_down and index_down and middle_down and ring_down and pinky_down

    def cal_distance(self, hand_list: list, point1, point2):
        x1 = hand_list[point1][1]
        y1 = hand_list[point1][2]
        x2 = hand_list[point2][1]
        y2 = hand_list[point2][2]
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

    def is_ten(self, hand_list: list):
        thumb_down = not self.is_thumb_up(hand_list)
        index_down = (not self.is_index_up(hand_list)) and (self.judge_y(hand_list, 7, 6) > 8)
        middle_down = not self.is_middle_up(hand_list)
        ring_down = not self.is_ring_up(hand_list)
        pinky_down = not self.is_pinky_up(hand_list)
        return thumb_down and index_down and middle_down and ring_down and pinky_down

    def is_ok(self, hand_list: list):
        if self.cal_distance(hand_list, 8, 4) < 25:
            ok_flag = True
        else:
            ok_flag = False
        middle_up = self.is_middle_up(hand_list)
        ring_up = self.is_ring_up(hand_list)
        pinky_up = self.is_pinky_up(hand_list)
        return ok_flag and middle_up and ring_up and pinky_up

    def get_gesture(self, hand_list: list):
        if self.is_one(hand_list):
            return 1
        elif self.is_two(hand_list):
            return 2
        elif self.is_three(hand_list):
            return 3
        elif self.is_four(hand_list):
            return 4
        elif self.is_five(hand_list):
            return 5
        elif self.is_six(hand_list):
            return 6
        elif self.is_seven(hand_list):
            return 7
        elif self.is_eight(hand_list):
            return 8
        elif self.is_nine(hand_list):
            return 9
        elif self.is_ten(hand_list):
            return 10
        elif self.is_ok(hand_list):
            return "ok"
        else:
            return "Unknown"


# 如果直接运行此模块，则执行原始功能演示
if __name__ == "__main__":
    wCam, hCam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    recognizer = GestureRecognizer()

    while True:
        success, img = cap.read()
        if success:
            img, gesture = recognizer.process_image(img)
            lmList = recognizer.find_position(img)
            # if len(lmList) != 0:
            #     print(recognizer.cal_distance(lmList, 8, 12))
            cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
