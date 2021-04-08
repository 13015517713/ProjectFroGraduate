import sys
import time
from Util import log,myRedis as rs
from sklearn import svm
import json
import os
import dataStore as ds
from joblib import dump,load

# 应该一个线程一个logger的，但是太复杂了
logger = log.getDefLogger()
kModelUpdate = 1 # 间隔多少次更新下Model


# 一个ads一个训练器，这里先保持环境不变，环境变化的话需要删除之前的训练器重新训练
class Trainer:
    def __init__(self, fromAds, dockerName):
        self._ads = fromAds
        # 初始化所有模型
        self._dockerName = dockerName
        self._regrList = [svm.SVR(gamma='auto') for i in range(len(dockerName)) ] 
        self._fitCnt = 0
    def fitAll(self, xList, yList): # 传入所有模型的X和Y
        self._fitCnt = self._fitCnt + 1
        for i in range(len(xList)):
            X = xList[i]
            Y = yList[i]
            self._regrList[i].fit([X],Y)
        logger.debug("Trainer train times=%s ads=%s"%(str(self._fitCnt),self._ads) )
        if self._fitCnt % kModelUpdate == 0:
            self.updateModel()
            logger.info("Trainer ads=%s update model."%(self._ads) )
    def updateModel(self):
        objdir = os.path.join(ds.kStoreRootPath, self._ads, "model")
        if not os.path.exists(objdir):
            os.makedirs(os.path.join(objdir))
        for i in range(len(self._dockerName)):
            objfile = os.path.join(objdir, "model_" + self._dockerName[i])
            dump(self._regrList[i], objfile)
    # 加载所有model
    def loadModel(self):
        objdir = sys.path.join(ds.kStoreRootPath, fromAds)
        if not os.path.exists(objdir):
            return
        for i in range(len(self._dockerName)):
            objfile = sys.path.join(objdir, "model_" + self._dockerName[i])
            tmodel = load(objfile)
            self._regrList[i] = tmodel
    def predictByName(self, dockername, X):
        if dockername in self._dockerName:
            ads = self._dockerName.index(dockername)
        else:
            return None
        return self._regrList[ads].predict([X])

# 存储所有训练器
TrainerList = {}

def run(timeInterval = 10):
    while True:
        logger.info("Start to run train.")
        # 从redis中取出来，然后拿进去训练
        '''
        1.拿出来一条数据 空或非空
        2.找Ads并初始化模型，
        '''
        res = rs.popFromList('MetricList')
        if res == None:
            time.sleep(timeInterval)
            continue
        allMetric = json.loads(res)
        dockerName = []
        X = []
        Y = []
        for metric in allMetric['trainData']:  # error
            dockerName.append(metric['dockerName'])
            X.append(metric['X'])
            Y.append(metric['Y'])
        fromAds = allMetric['fromAds']
        if fromAds not in TrainerList:
            TrainerList[fromAds] = Trainer(fromAds, dockerName)
        # 开始fit
        trainer = TrainerList[fromAds]
        logger.info("Start fit all X=",X,' and Y=',Y)  # 不符合logger的格式
        trainer.fitAll(X,Y)

        time.sleep(timeInterval)
        
if __name__ == '__main__':
    # run()
    fromAds = '127.0.0.1'
    dockerName = ['redis','mcf','bzip']
    xList = [[0,1],[1,0],[2,1]]
    yList = [[0],[1],[2]]
    trainer = Trainer(fromAds, dockerName)
    trainer.fitAll(xList, yList)
    print(trainer.predictByName('mcf',[0,1]))
    objfile = '/home/wcx/gitProject/projectFroGraduate/QosMaster/data/model/testModel'
    # with open(objfile) as r:
    dump(trainer, objfile)
    trainer = load(objfile)
    print(trainer.predictByName('redis',[0,1]))