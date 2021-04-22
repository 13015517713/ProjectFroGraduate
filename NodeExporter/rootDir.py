import numpy as np
import os
from Util import config,log
import json
import csv
import subprocess

logger = log.getDefLogger()
kNeedAppName = ["bzip","redis","mcf","spec"] # 过滤其他docker
kMainAppName = ["redis"]

def getMainApp():
    return kMainAppName

def isNeed(dockername):
    if dockername in kNeedAppName:
        return True
    return False

def isMain(dockername):
    if dockername in kMainAppName:
        return True
    return False

# 从该目录下的task拿到PID列表
def getPIDFromDir(rootPath):
    filename = os.path.join(rootPath, "tasks")
    taskfile = open(filename, "r")
    # 得到
    taskPids = []
    reader = csv.reader(taskfile)
    for pid in reader:
        taskPids.append(pid[0])
    taskfile.close()
    return taskPids

# 拿到Proc目录进程ID列表
def getPIDFromDirProc(rootPat)
    filename = os.path.join(rootPath, "cgroup.procs")
    taskfile = open(filename, "r")
    taskPids = []
    reader = csv.reader(taskfile)
    for pid in reader:
        taskPids.append(pid[0])
    taskfile.close()
    return taskPids

# docker inspect得到信息
def getDockerDataFromID(dockerid):
    cmd = "sudo docker inspect %s"%(dockerid)
    res = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=False)
    if res.returncode !=0:
        logger.fatal("Can't find docker %s when docker inspect"%(dockerid) )
        raise Exception("Can't find docker %s when docker inspect"%(dockerid) )
        return None
    formatData = json.loads(res.stdout)
    logger.debug("Docker inspect %s name=%s."%(dockerid,formatData[0]["Name"]))
    return formatData[0]

class Docker:
    def __init__(self, rootPath, dockerid):
        self._rootPath = rootPath
        self._pids = getPIDFromDir(rootPath) # 得到Pid列表
        self._pidsExceptLwp = getPIDFromDirProc(rootPath)
        self._id = dockerid
        self._meta = getDockerDataFromID(dockerid)
    def getPidExceptLwp(self):
        self._pidsExceptLwp = getPIDFromDirProc(self._rootPath)
        return self._pidsExceptLwp
    def getPids(self):
        # 可能Pid发生变化，选哟更新
        self._pids = getPIDFromDir(self._rootPath)
        return self._pids
    def getGroup(self):
        return "docker" + "/" + self._id
    def getName(self):
        return self._meta["Name"].replace("/",'')
    def getId(self):
        return self._id

# 存储rootDir中所有Pod
class RootDir:
    def __init__(self, kRootPath, kToFind="docker"):
        self._rootPath = kRootPath
        self._savedDockerID = []
        self._dockerAll = []
        self._toFind = kToFind
        self._added = []
        self._subed = []

    def getAllDocker(self):
        return self._dockerAll
    def getAlladded(self):
        return self._added
    def getAllsubed(self):
        return self._subed
    def popAlladded(self):
        # copy一份返回，不然返回的是引用
        added = self._added
        self._added = []
        return added
    def popAllsubed(self):
        subed = self._subed
        self._subed = []
        return subed

    # 扫当前目录所有toFind,更新subed和added
    def load(self): # 更新目录
        updatelen = 0
        findflag = np.zeros(len(self._savedDockerID) )
        dirFiles = os.listdir(self._rootPath)
        nowDocker = []
        nowDockerID = []
        for i in range(len(dirFiles)):
            sfile = dirFiles[i]
            sfilepath = os.path.join(self._rootPath, sfile)
            if os.path.isdir(sfilepath): # finddocker
                nowDockerID.append(sfile)
                index = self._savedDockerID.index(sfile) if (sfile in self._savedDockerID) else -1
                if index == -1: # 之前没有
                    logger.info("Find a new application %s"%(sfilepath) )
                    docker = Docker(sfilepath, sfile)
                    nowDocker.append(docker)
                    self._added.append(docker)  # 添加新增的
                    updatelen += 1
                else: # 之前存在
                    findflag[index] = 1
                    nowDocker.append(self._dockerAll[index])
        # 添加减少的
        for i in range(len(findflag) ):
            found = findflag[i]
            if found == 0:
                updatelen += 1
                self._subed.append(self._dockerAll[i])

        self._savedDockerID = nowDockerID
        self._dockerAll = nowDocker
        return updatelen


if __name__ == '__main__':
    dockerid = "ede1831d26927b7aee224af215f2df702bf3e10c192f6534c44602ca1e07b407"
    # getDockerNameFromID(dockerid)
    rootDir = config.getConfig("rootDir")
    docker = Docker(rootDir, dockerid)
    print(docker.getName() )
