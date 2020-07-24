import cv2
import json
import numpy as np

if __name__ == "__main__":
    # 视频的宽度和高度
    width = 16
    height = 12

    # 读入视频，初始化参数
    cap = cv2.cv2.VideoCapture("badapple.mp4")
    success = True
    frameCnt = 0

    # 初始化记录，二维数组中每个点表示一个灯30帧的状态
    recordNum = np.zeros((height, width), dtype='uint32')
    # 每个元素表示1秒记录
    records = []

    while success:
        # 读取一帧图像
        success, frame = cap.read()
        if success:
            # 缩小图像
            frame = cv2.cv2.resize(frame, (width, height))
            # 转灰度图
            grayFrame = cv2.cv2.cvtColor(frame, cv2.cv2.COLOR_RGB2GRAY)
            # 转二值图，因为Bad Apple中又阴影，所以谨慎设置阈值（其实随手设置的）
            binFrame = cv2.cv2.threshold(grayFrame, 200, 1, cv2.cv2.THRESH_BINARY)

            # 转成uint32的np.array
            binImg = np.array(binFrame[1], dtype='uint32')
            # 记录到数字中，越早的帧存储在越低的位
            recordNum ^= (binImg<<(frameCnt%30))
            # 帧计数加1
            frameCnt += 1
        if frameCnt % 30 == 0:
            # 当完成了30帧计数后，将数据转成list存储，此时recordNum是12个，
            # 每个元素长度位16的二维数组，而为了方便，需要16个，每个元素长度
            # 为12的二维数组（读一个数组，存到一个常量运算器中），因此转置
            record = recordNum.T.tolist()
            # 添加1秒记录
            records.append(record)
            # 记录清零
            recordNum = np.zeros((height, width), dtype='uint32')
    # 导出数组为json
    js = json.dumps(records, indent=2)
    # 存文件
    with open('tmp.txt', 'w', encoding='utf-8') as f:
        f.write(js)