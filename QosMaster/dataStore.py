# 用于存储Docker/Pod信息
'''
    考虑训练模型多开一个线程
'''
import numpy as np
import csv
import sys
import os
from Util import log

logger = log.getDefLogger()
allMechs = {} # ads对应mecg列表
kStoreRootPath = "/home/wcx/gitProject/projectFroGraduate/QosMaster/data/"
# 每个应用的指标都拿到
kMainExTar = ["lock_loads","fp_uops","branch","l1_misses","l2_misses","stall_sb","branch_misp","machine_clear"]
kSubTar = ["instructions","cycles","loads_and_stores","cache-misses"]

class Docker:
    def __init__(self, dockerid, dockername):
        self._history = []
        self._nowdata = []
        self._dockerid = dockerid
        self._name = dockername
    def addMetric(self, data): # 本身自己做同步互斥
        self._nowdata.append(data)
        self._history.append(data)
    def popMetric(self, data):
        # 弹出第一个
        someData = self._nowdata
        self._nowdata = []
        return someData
    def getName(self):
        return self._name

class Mechine:
    def __init__(self, ads):
        self._ads = ads
        self._dockers = []
    def getAds(self):
        return self._ads
    def findDockerByName(self, dockername):
        for docker in self._dockers:
            if dockername == docker.getName():
                return True
        return False
    def addDocker(self, dockername, dockerid):
        self._dockers.append(Docker(dockerid,dockername) )
    def getAllDocker(self):
        return self._dockers

def addDocker(fromAds, dockerid, dockername):
    if fromAds not in allMechs:
        logger.info("Find new docker source ads=%s"%(fromAds))
        Mech = Mechine(fromAds)
        allMechs[fromAds] = Mech
    else:
        Mech = allMechs[fromAds]
    if Mech.findDockerByName(dockername):
        logger.warning("Docker name=%s has been registered."%(dockername))
    else:
        Mech.addDocker(dockername, dockerid)
    return

def logoutDocker(fromAds, dockerid, dockername):
    if fromAds not in allMechs:
        return
    Mech = allMechs[fromAds]
    allDockers = Mech.getAllDocker()
    for i in range(len(allDockers) ):
        docker = allDockers[i]
        if docker.getName() == dockername:
            # 模型线程可能正在使用，不能直接del
            allDockers[i] = None
            del allDockers[i]
            logger.debug("Logout docker name=%s."%(dockername))
            break

# 向docker中添加一个指标，如果目前没存这个docker重新创建对象存
def pushMetric(fromAds, dockername, dockerid, metric):
    # 主指标放进去
    data = []
    for tmetric in kMainExTar:
        if tmetric in metric:
            data.append(float(metric[tmetric]))
        else:
            data.append(float(0.0) )
    for tmetric in kSubTar:
        if tmetric in metric:
            data.append(float(metric[tmetric]))
        else:
            data.append(float(0.0) )
    if fromAds not in allMechs:
        logger.warning("Get metric dockername=%s without mechine registered from %s."%(dockername,fromAds) )
        Mech = Mechine(fromAds)
        allMechs[fromAds] = Mech
    else:
        Mech = allMechs[fromAds]
    allDockers = Mech.getAllDocker()
    # 先在已有机器中查找
    found = False
    for docker in allDockers:
        if docker.getName() == dockername:
            found = True
            docker.addMetric(metric)
    if not found:
        logger.warning("Get metric dockername=%s without docker registered from %s."%(dockername, fromAds) )
        docker = Docker(dockerid, dockername)
        docker.addMetric(metric)
        Mech.addDocker(docker)
    # 写入文件 data/ip/dockername：首行为指标名称，下面是指标
    pushToFile(fromAds, dockername, data)
    # 写入完毕后 写入redis，训练线程会去读然后加入训练
    '''
    '''

# 以csv的方式写进去，每次写之前都清空
def pushToFile(fromAds, dockername, data):
    objdir = os.path.join(kStoreRootPath,fromAds)
    # dockername以/开头的话，拼接就从dockername开始了，从最后一个/的开始
    if dockername.find('/') != -1:
        dockername = dockername.replace('/','-')
    objfile = os.path.join(objdir, dockername) # 拼接从第一个/开始这个
    if not os.path.exists(objdir):
        os.makedirs(os.path.join(kStoreRootPath,fromAds))
    if not os.path.exists(objfile): # 第一次写文件就打开文件
        tfile = open(objfile, "w")
        twriter = csv.writer(tfile)
        twriter.writerow(kMainExTar + kSubTar)
    else:
        tfile = open(objfile, "a")
        twriter = csv.writer(tfile)
    twriter.writerow(data)
    logger.debug("Dockername=%s ads=%s writeToFiles successfully."%(dockername,fromAds) )
    tfile.close()

def checkAllMetric(allMetric):
    for oneMetric in allMetric:
        maxData = 0
        for metric in oneMetric['dockerMetric'].values():
            maxData = max(maxData, float(metric))
        if maxData <= 0:
            logger.warning("One docker maxMetric is zero.Maybe not running.")
            raise ValueError("MaxMetric is zero.Please check docker is running.")
    return

if __name__ == '__main__':
    pushToFile("10.118.0.224", "test", [2222,23])