import requests
import json
import sys
sys.path.append('..')
from Util import log

logger = log.getDefLogger()

# data必须为字典结构
def sendHttpByGet(url, data):
    tinfo = 1
    obj = url + '?'
    index = 0
    tlen = len(data)
    for key in data.keys():
        index += 1
        obj += str(key) + '=' + str(data[key]) 
        if index != tlen:
            obj += '&'
    logger.debug("Send to url=%s"%(obj))
    return requests.get(obj)

# key携带data这个数据
def sendHttpByPost(url, key, data):
    logger.debug("Send to url=%s and data=%s"%(url, str(data)) )
    return requests.post(url, json={key:data})

if __name__ == '__main__':
    url = 'http://127.0.0.1:8000/tranMetric'
    sendHttpByPost(url, 'data', {'data':10})
    # data = {"data":10, "data2":11}
    # sendHttpByPost(url, 'data', data)
