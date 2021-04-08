# redis库实现存储数据和拿出来数据训练
import sys
sys.path.append("..")
import redis
from Util import config
import json

r = redis.Redis(host=config.getConfig('RedisServer'), port=int(config.getConfig('RedisPort')), db=0)

def pushToList(key, value):
    r.lpush(key, value)
    return

def popFromList(key):
    res = r.rpop(key)
    return res

# 清空list
def clearList(key):
    res = r.rpop(key)
    while res != None:
        res = r.rpop(key)

if __name__ == '__main__':
    clearList('list')
    X = [1,2,3,4]
    Y = [3]
    data = [{"X":X,"Y":Y}]
    trainList = {"trainData":data}
    print(json.dumps(trainList) )
    pushToList('list',json.dumps(trainList))
    res = popFromList('list')
    data = json.loads(res)
    print(data["trainData"][0]["Y"])