import pyautogui
from time import sleep

import data

if __name__ == "__main__":
    # 屏幕大小，我的电脑是1366*768
    width, height = pyautogui.size()
    # 鼠标的位置，"home"为点击常量运算器的位置
    # "const"为选择信号的位置，这里在蓝图的时候就确定好常量运算器中有哪些信号了
    # "count"为输入数量的位置
    mousePos = {
        "home": {
            "x": width//2,
            "y": height//2 - 50
        },
        "const": {
            "X": [590, 627, 664, 701, 738, 775],
            "Y": [365, 402, 439]
        },
        "count": {
            "x": 787,
            "y": 482
        }
    }
    # 跑路的时间长短，"main"：走到下一个常量运算器需要的时间
    # "goBack"：从最后一个常量运算器返回到向下行进的起点的时间
    # "nextLine"：向下走的时间
    # "return"：走到下一行中的起始位置需要的时间
    sleepTime = {
        "main": 0.01,
        "goBack": 2.1,
        "nextLine": 0.25,
        "return": 0.32
    }
    # 准备
    sleep(3)
    for i in range(10, 20):
        # 可以手动微调位置
        sleep(1)
        for j in range(data.width):
            # 移动当前的常量运算器
            pyautogui.moveTo(mousePos["home"]["x"], mousePos["home"]["y"])
            # 点进设置界面
            pyautogui.click()
            for k in range(data.height):
                x = k%6
                y = k//6
                # 移动到某个信号框
                pyautogui.moveTo(mousePos["const"]["X"][x], mousePos["const"]["Y"][y])
                # 选择信号框
                pyautogui.click()
                # 移动到数据设定区域
                pyautogui.moveTo(mousePos["count"]["x"], mousePos["count"]["y"])
                # 聚焦数据设定区域
                pyautogui.click()
                # 删除原来的0
                pyautogui.press('backspace')
                # 设置成新的数值
                pyautogui.typewrite(str(data.data[i][j][k]))
            # 退出信号设定
            pyautogui.press('e')

            # 到下一个常量运算器
            pyautogui.keyDown('d')
            sleep(sleepTime["main"])
            pyautogui.keyUp('d')

        # 返回准备走向下一层
        pyautogui.keyDown('a')
        sleep(sleepTime["goBack"])
        pyautogui.keyUp('a')
        # 走向下一层并准备走到初始位置
        pyautogui.keyDown('s')
        sleep(sleepTime["nextLine"])
        pyautogui.keyUp('s')
        # 走到初始位置
        pyautogui.keyDown('d')
        sleep(sleepTime["return"])
        pyautogui.keyUp('d')
