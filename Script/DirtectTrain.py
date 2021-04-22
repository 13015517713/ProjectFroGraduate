# 直接拿数据直接进行训练
'''
实现：
1.指定数据路径、训练对象
2.然后直接对数据进行训练，得到模型
3.画图对比数据 (当然这个要运行在windows上)
'''
import os
import matplotlib as mt
import csv
from sklearn import svm
from joblib import dump,load
import logging

logger = logging.getLogger()
kNameList = ['spec','redis','mcf','bzip']
kDataPath = '/home/wcx/gitProject/projectFroGraduate/Script/data/'
kTrainDataPath = '/home/wcx/gitProject/projectFroGraduate/Script/dataForTrain/'

def getTrainDataByName(name, rootPath):
    resfile = os.path.join(rootPath, "trainData_"+name)
    if os.path.exists(resfile) and os.path.isfile(resfile):
        tfile = open(resfile, "r")
    else:
        return None,None
    treader = csv.reader(tfile)
    X = []
    Y = []
    for onedata in treader:
        X.append(onedata[:-1])
        Y.append([onedata[-1]])
    return X,Y

if __name__ == '__main__':
    data = {}
    
    # 用训练数据训练模型
    model = [svm.SVR() for i in range(len(kNameList))]
    for i in range(len(kNameList)):
        name = kNameList[i]
        xlist,ylist = getTrainDataByName(name, kDataPath)
        if xlist == None:
            logger.fatal("%s has no data."%(name) )
        data[name] = {}
        model.fit(xlist,ylist)

    # 用测试数据得到newYlist
    
    for i in range(len(kNameList)):
        name = kNameList[i]
        xlist,ylist = getTrainDataByName(name, kTrainDataPath)
        data[name] = {}
        newYlist.append(ylist)


    # 下面再跑一些测试数据，然后输出ipc对比
