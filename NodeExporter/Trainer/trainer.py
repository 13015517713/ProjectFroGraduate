import sys

# 1.负载自动预测的实现
# 2.负载分类的实现
# 3.目前只限制CPU

mainApp = None

# 形式dockername:CPU,Mem列表
topData = {}

# 时间窗口大小/s，用来预测的
timeWindows = 10

# 设置主应用
def setMainAppName(appName):
    global mainApp
    mainApp = appName

def pushTopData(dockername, topdata):
    if dockername not in topData:
        oneDocker = {"cpu":[],"mem":[]}
        topData[dockername] = oneDocker
    cpu = float(topdata["cpu"])
    mem = float(topdata["mem"])
    topData[dockername]["cpu"].append(cpu)
    topData[dockername]["mem"].append(mem)

# 得到主应用在时间序列中最小的负载大小，这个格式是cpu%,mem% cpu和mem的使用率大小
def getPredMinRemain():
    pass

# 核心函数，我想知道我现在BE可以运行多少。
# 1.小于SLO（此时不可接收BE）
#  1.1小于SLO，但是有BE在运行
#   1.1.1 只有一个BE，看是否是最低资源水位，是最低就迁移，不是最低，就降到最低
#   1.1.2 多个BE在运行，将BE都打压到最低资源水位，如果都是最低的资源水位，依次对资源占用最大的BE进行迁移，调度周期自己设定
#  1.2小于SLO，没有BE，警报
# 2.模型刚开始建立（小于设置的训练时间阈值）
#  2.1继续训练，不接受BE
#  2.2在这个场景下，是否可以autoSLO？  侵入式的，非侵入式的？ 
    # 我们假定运维都十分了解这个应用，配的资源足够使用。那我们直接要求SLO大于正常情况的正态分布的边缘值即可
# 3.模型初步形成，还不够完善，可调度BE加入，然后开始运行混部（可以有条件接收BE）
#  3.1如果SLO满足要求，发出可接收信号，分发器给我BE，按照当前预测的最低水位运行，继续运行，发现对SLO没有影响，尝试增加BE水位，如果BE没有完全使用资源，继续发送分发器信号，重复流程
# 4.模型已经完成训练，准确率已经达到设定值
#  4.1尝试减少预测窗口的大小，更细粒度对资源进行调控，逐步变小

def getAdvice():
    pass