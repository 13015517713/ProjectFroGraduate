# redis库实现存储数据和拿出来数据训练
import sys
sys.path.append("..")
import redis
from Util import config

r = redis.Redis(host=config.getConfig('RedisServer'), port=int(config.getConfig('RedisPort')), db=0)

def pushToList(key, value):
    r.lpush(key, value)
    return

def popFromList(key):
    res = r.rpop(key)
    return res

if __name__ == '__main__':
    setValue('test', "1")
    print(getValue('test'))