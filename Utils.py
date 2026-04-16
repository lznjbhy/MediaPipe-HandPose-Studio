import cv2

# 读取图片
background = cv2.imread('C:/Users/ZJH\Desktop/Resources/Background.png')  # 背景大图
overlay = cv2.imread('C:/Users/ZJH/Desktop/Resources/logo-NBA.jpg')  # 小图

# 设置小图的位置（比如左上角坐标为 (100, 100)）
x, y = 420, 200

# 获取小图尺寸
h, w = overlay.shape[:2]

# 检查小图是否会越界（可选）
if y + h > background.shape[0] or x + w > background.shape[1]:
    raise ValueError("小图超出背景图范围，请调整位置或尺寸")

# 覆盖粘贴
background[y:y + h, x:x + w] = overlay

# 保存新图片
cv2.imwrite('combined.jpg', background)

print("新图片已生成并保存为 combined.jpg")


