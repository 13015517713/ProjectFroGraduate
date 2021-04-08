# 用于存储Docker/Pod信息
'''
    考虑训练模型多开一个线程
'''
import numpy as np
import csv
import sys
import os
import json
from itertools import chain
import training as train
from Util import log,myRedis as rs

logger = log.getDefLogger()
allMechs = {} # ads对应mecg列表
kStoreRootPath = "/home/wcx/gitProject/projectFroGraduate/QosMaster/data/"
# 每个应用的指标都拿到
kMainExTar = ["lock_loads","fp_uops","branch","l1_misses","l2_misses","stall_sb","branch_misp","machine_clear"]
kSubTar = ["instructions","cycles","loads_and_stores","cache-misses"]
kNeedAppName = ["bzip","redis","mcf","spec"] # 过滤其他docker
kMainAppName = ["redis"]

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
    def addDocker(self, docker):
        self._dockers.append(docker )
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

# 以csv的方式写进去，每次写之前都清空
def pushToFile(fromAds, dockername, data):
    objdir = os.path.join(kStoreRootPath,fromAds)
    # dockername以/开头的话，拼接就从dockername开始了，从最后一个/的开始
    if dockername.find('/') != -1:
        dockername = dockername.replace('/','-')
    objfile = os.path.join(objdir, dockername) # 拼接从第一个/开始这个
    if not os.path.exists(objdir):
        os.makedirs(os.path.join(objdir))
    # 第一次写文件就打开文件
    if not os.path.exists(objfile):
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

# 把Metric包装下，写到redis中(需要序列化)
# redis报文格式： fromAds=fromAds,data=[[dockername,[X],[Y]],]
def pushToRedis(fromAds, trainData):
    # trainData是个列表
    tranData = {'trainData':trainData, 'fromAds':fromAds}
    rs.pushToList('MetricList', json.dumps(tranData))

# 将要训练的数据写入文件
def trainDataToFile(fromAds, dockername, X, Y, title):
    objdir = os.path.join(kStoreRootPath,fromAds)
    # dockername以/开头的话，拼接就从dockername开始了，从最后一个/的开始
    if dockername.find('/') != -1:
        dockername = dockername.replace('/','-')
    objfile = os.path.join(objdir, "trainData_" + dockername) # 拼接从第一个/开始这个
    if not os.path.exists(objdir):
        os.makedirs(os.path.join(kStoreRootPath,fromAds))
    if not os.path.exists(objfile): # 第一次写文件就打开文件
        tfile = open(objfile, "w")
        twriter = csv.writer(tfile)
        twriter.writerow(title + [dockername + '_ipc'])
    else:
        tfile = open(objfile, "a")
        twriter = csv.writer(tfile)
    twriter.writerow(X+Y)
    logger.debug("Dockername=%s ads=%s trainData writeToFile successfully."%(dockername,fromAds) )
    tfile.close()

# 整理数据，返回[fromAds,name,[X],[Y]]的列表，并写入文件
def dealData(fromAds, allMetric):
    dataList = []
    dockerName = []
    mainMetricList = []
    subMetricList = []
    mainTitleList = []
    subTitleList = []
    ipcList = []
    for metric in allMetric:
        dockername = metric['dockerName']
        dockerName.append(dockername)
        dockerMetric = metric['dockerMetric']
        mainMetric = []
        subMetric = []
        ipc = float(dockerMetric["instructions"]) / float(dockerMetric["cycles"])
        ipcList.append(ipc)
        mainTitle = [dockername+"_"+r for r in kMainExTar]
        subTitle = [dockername+"_"+r for r in kSubTar]
        for i in kMainExTar:
            if i in dockerMetric:
                mainMetric.append(float(dockerMetric[i]) )
            else:
                mainMetric.append(0)
        for i in kSubTar:
            if i in dockerMetric:
                subMetric.append(float(dockerMetric[i]) )
            else:
                subMetric.append(0)
        mainTitleList.append(mainTitle)
        subTitleList.append(subTitle)
        mainMetricList.append(mainMetric)
        subMetricList.append(subMetric)

    for i in range(len(dockerName) ):
        dockername = dockerName[i]
        # data = {'fromAds':fromAds}
        data = {}
        data['dockerName'] = dockername
        # 后面两项二维变成一维
        X = mainMetricList[i] \
            + [ii for jj in subMetricList[0:i] for ii in jj] \
            + [ii for jj in subMetricList[i+1:] for ii in jj]
        Y = [ipcList[i]]
        data['X'] = X
        data['Y'] = Y
        dataList.append(data)
        title = mainTitleList[i]  \
            + [ii for jj in subTitleList[0:i] for ii in jj] \
            + [ii for jj in subTitleList[i+1:] for ii in jj]
        # 将数据和Title写入文件
        trainDataToFile(fromAds, dockername, X, Y, title)
    
    return dataList

if __name__ == '__main__':
    allMetric =[
         {'dockerName': 'mcf', 'dockerId': 'aed4f49e2cf9f013d3e793455b5909106da365839eecf02b41915d53d6eda26a', 'dockerMetric': {'ipc': 31.22, 'instructions': 3659853317.0, 'cycles': 10898601734.0, 'loads_and_stores': 1598972743.0, 'cache-misses': 261432576.0, 'lock_loads': 42044.0, 'fp_uops': 8.0, 'branch': 1114110330.0, 'l1_misses': 537615167.0, 'l2_misses': 356674700.0, 'stall_sb': 3844770.0, 'branch_misp': 42307694.0, 'machine_clear': 283481.0, 'idq_uops_not_delivered.core': 1655918950.0, 'uops_issued.any': 6124006908.0, 'uops_retired.retire_slots': 3135004538.0, 'int_misc.recovery_cycles': 240259539.0}}, 
         {'dockerName': 'bzip', 'dockerId': '54035d78f8da3a5ff306bad649c3f014ee01534e3d3fd721267331fe6c163f98', 'dockerMetric': {'ipc': 31.22, 'instructions': 15803997536.0, 'cycles': 10900853448.0, 'loads_and_stores': 6723490635.0, 'cache-misses': 941405.0, 'lock_loads': 41017.0, 'fp_uops': 8.0, 'branch': 2481902563.0, 'l1_misses': 136494582.0, 'l2_misses': 64000996.0, 'stall_sb': 451053221.0, 'branch_misp': 176458177.0, 'machine_clear': 427495.0, 'idq_uops_not_delivered.core': 5595834973.0, 'uops_issued.any': 26223557526.0, 'uops_retired.retire_slots': 15452838812.0, 'int_misc.recovery_cycles': 1005250617.0}}, 
         {'dockerName': 'redis', 'dockerId': '7f96329d3a633624d9a841b5b4f4c87514b7d6c86ff74426f793f53f39448e1f', 'dockerMetric': {'ipc': 34.88, 'instructions': 1543979.0, 'cycles': 3165260.0, 'loads_and_stores': 716177.0, 'cache-misses': 28533.0, 'lock_loads': 4356.0, 'fp_uops': 101.0, 'branch': 309717.0, 'l1_misses': 25975.0, 'l2_misses': 19440.0, 'stall_sb': 57107.0, 'branch_misp': 4757.0, 'machine_clear': 108.0, 'idq_uops_not_delivered.core': 6960161.0, 'uops_issued.any': 2185188.0, 'uops_retired.retire_slots': 2073802.0, 'int_misc.recovery_cycles': 33853.0}}
    ]
    dealData("127.0.0.1", allMetric)
    # pushToFile("10.118.0.224", "test", [2222,23])

    # t = [1,2,3]
    # tt = [r for i in [[1,1], [2,2]] for r in i]
    # tt = [[1,2,], [3], [4]]
    # print(list(chain(*tt)) )