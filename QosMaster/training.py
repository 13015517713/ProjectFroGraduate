import sys
import time
from Util import myRedis 
from sklearn import svm

# 一个ads一个训练器，这里先保持环境不变，环境变化的话需要删除之前的训练器重新训练
class Trainer:
    def __init__(self, fromAds, ):
        self._ads = fromAds
        self._regrList = []
        
    def allFit(self, xList, yList): # 传入所有模型的X和Y
        

# 存储所有训练器
TrainerList = {}

def run(timeInterval = 10):
    while True:
        # 从redis中取出来，然后拿进去训练
        '''
        1.拿出来一条数据 空或非空
        2.找Ads并初始化模型，
        '''
        time.sleep(timeInterval)
        
if __name__ == '__main__':
    run()