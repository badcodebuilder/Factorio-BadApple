# Bad Apple in Factorio

有屏幕的地方就有Bad Apple，本项目主要包括了以下几部分：

+ 原理与结构介绍
+ 相关代码

成品视频已经上传到[bilibili](https://www.bilibili.com/video/BV1jz4y1Q7fT/)上了哦，记得三连（up主脸皮厚如城墙）

游戏版本：Factorio 0.16.3

## 原理与结构介绍

### 显示

该思路的灵感来源于贴吧某位大佬的跑马灯蓝图，有幸下载到蓝图并（假装）分析了一下，发现用到了**移位**，并且灯阵是按列分的，而且每个灯点亮的**信号以及条件都不一样**，这一点启发了我，于是我做出了如下的一个设计：

```text
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light01
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light02
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light03
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light04
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light05
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light06
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light07
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light08
0b0001 0101 1010 1111 0001 0101 1010 1111 -> Light09
```

简单解释一下就是：用一个32位数来表示一个灯在32帧里面的状态，第n帧状态只需要右移n位然后取最低位就可以了。又因为游戏存在的一下设定：

1. 一条信号线里面可以传输多个信号
2. 一个信号可以用一个32位带符号整数表示数量（也可以理解成强度之类的）
3. 一个算数处理器可以接受一条线中的所有信号作为红（绿）输入，并对每一个信号进行相同的操作，并在红（绿）输出上输出所有信号对应的结果

单列（这里转成行节约篇幅）如下图所示：

![line](img/line.png)

共有12个灯，从左往右第k个灯点亮的条件就是signal-k > 0，例如第0个灯就是signal-0 > 0，第10个灯就是signal-A > 0。

12个信号最右侧输入进来（我是从红线输入），右移n位（n也是一个输入，我是从绿线输入），从红线输出右移n位后12个信号的结果。再全部输入按位与操作，与1进行按位与获得12个信号的最低位，从红线输出链接到灯上。最后按照灯上的逻辑亮灯即可显示图片的一列。

最终灯阵如下图：

![mat](img/mat.png)

实际操作中我只用了30位信号来表示1秒内的状态，因为视频是30fps的，一个常量存储器刚刚好。

另外为什么是16\*12，因为两个广域配电站之间的最大距离就是16格，Bad Apple的长宽比是4:3，因此设置为16\*12，如果更改游戏数据，扩大配电范围和增加连线长度，由于一个常量存储器可以存储18个信号，所以可以做成24\*18的灯阵。此外，如果可以的话还可以用多个灯阵拼接成一个更大的灯阵，分辨率更高，但是运算器与存储器的排列就会错开了，强迫症患者表示很难受。

### 存储

一个常量存储器只能存储一列的30帧数据，整个画面的30帧需要16个常量存储器，那么难题来了，现在需要一个常量存储器数组来存储每列219秒信号常量，并且**能按序读出**。主要是后面的这个要求难一点。思考了10分钟，做出了如下设计：

![array](img/array.png)

该图为设计的简化模型，这是一个长度为4的数组，从左到右判断运算器输出的条件为：第t个判断运算器输入的signal-T = t，例如第0个判断运算器输出条件为signal-T = 0。

每个判断运算器的红输入为常量存储器中的信号，绿输入为一个时间相关的信号，例如上文中用的signal-T。输出信号选择原始信号（即红绿线信号的总和），并将输出信号并联成一个总的输出。因为符合输出条件才输出，所以这个数组中至多只会输出1个常量存储器中的信号。

> 警告：这里比较运算器中红线和绿线的输入千万不能有相同的信号（除非你知道你在干什么），否则相同的信号会进行相加再输出，常量存储器中存的视频数据就被污染辣。

将该结构变成一列（这里用一行来节省空间）：

![arrayline](img/arrayline.png)

组成二维数组（片段）：

![dataMat](img/arraymat.png)

> 提示：这里可能和上面一幅图有一些出入，但是原理是一样的，所有的绿线输入都是相同的、与实践相关的信号，我为了减少线的长短就这样排列了。比较运算器每行的参数都是相同的，一列中才按照0~219排列。

### 计数信号

这就很简单了，加法器将输入信号和输出信号（需要相同）连接起来，每次加1就成了计数信号，每秒钟大约计数60次，可以用整除来实现分频。如下图：

![count](img/count.png)

该图中上面一行中，最右是计数信号，把绿色输入输出连接起来即可。右二是调节计数速度的调节器，用于debug的时候1/n倍速计数。

上面一行右三是除以2，可以使得信号每2/60秒加1（在调节器为1倍速的时候）。右四是模30，可以产生0~30的输出信号，表示位移的位数。

下面一行是除以60，可以使得信号每60/60秒加1（在调节器为1倍速的时候），输出秒数信息。

### 整体连接

整体连接如下图：

![general](img/general.png)

+ 计数信号与显示：位移位数信号接入显示绿线输入
+ 计数信号与存储：秒数信息接入存储判断运算器绿线输入
+ 存储与显示：某列存储红线输出接入对应列显示红线输入

## 相关代码

### 视频处理

主要工作：抽帧、缩小、压缩成二进制数据等工作，具体看[代码](genSeq.py)注释

### 输入参数

主要工作：设置常量存储器、判断运算器的参数（太辛酸了），具体看[代码](main.lua)注释

一个常量存储器要输入12个信号，每个信号还要输入特定的数字，一共16\*219个常量存储器，不批量操作肯定不行。但是又看不懂它的API，怎么办？只能用最原始的办法键盘鼠标模拟器——站在特定的起点，设置常量存储器的信号、调整数量、退出、跑到下一个，循环完一层跑回来，跑到下一层开始点，继续循环。

设了20行，发现问题还是很严重，一方面设置一行需要2分钟，219行需要7小时多，另一方面更严重的是，走路的时间虽然是固定的，但是并不能走到理想的位置，误差一旦积累，错一格就连着错下去了，而且如果撞到石头或者配电站走不动，那就更加凉凉了。

[代码](setData.py)大家就乐呵一下，屏幕分辨率是1366\*768，游戏放缩到最大，不穿任何外骨骼模块，初始位置为最左侧常量存储器的正下方。

最终被逼无奈，还是选择了内置的API，看了一晚想了半宿，调了一小时才设置完成所有参数。

## 后续

视频里面的BGM还是后期加上去的，想自己搞一个，但是还是挺麻烦的，还是等等再搞吧

提前祝Factorio 1.0诞辰快乐
