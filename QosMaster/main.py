import sys
# print(sys.path)
from Util import log,config,myRedis as redis
from flask import Flask,request
import dataStore as ds
import json
import training as train
import threading

logger = log.getDefLogger()
app = Flask("QosMaster")

@app.route('/', methods=['GET','POST'])
def sayHello():
    # 提示用法
    return 'hello'

# 注册docker
@app.route('/register', methods=['GET'])
def register():
    fromAds = request.remote_addr
    dockername = request.args.get('dockername')
    if dockername not in ds.kNeedAppName:
        return 'can"t register'
    dockerid = request.args.get('dockerid')
    logger.info("Get register info dockername=%s from %s"%(dockername, fromAds) )
    ds.addDocker(str(fromAds), dockerid, dockername)
    return 'register'

@app.route('/logout', methods=['GET'])
def logout():
    fromAds = request.remote_addr
    dockername = request.args.get('dockername')
    if dockername not in ds.kNeedAppName:
        return 'can"t logout'
    dockerid = request.args.get('dockerid')
    logger.info("Get logout info dockername=%s from %s"%(dockername, fromAds) )
    ds.logoutDocker(str(fromAds), dockerid, dockername)
    return 'logout'

# 收集到的指标组装成向量加入对应docker的信息
@app.route('/tranMetric', methods=['POST'])
def getMetric():
    fromAds = request.remote_addr
    tinfo = request.get_json()
    allMetric = json.loads(tinfo['data'])
    try:
        logger.debug(allMetric)
        if ds.checkAllMetric(allMetric):
            pass
    except Exception as e:
        logger.warning(e)
        logger.warning("TranMetric gets one errordata.")
        return 'oneMetricRejected'
    # 写到docker&文件中
    for metric in allMetric:
        if metric['dockerName'] not in ds.kNeedAppName:
            continue
        ds.pushMetric(fromAds, metric['dockerName'], metric['dockerId'], metric['dockerMetric'])
    # 写到redis中
    ds.pushToRedis(fromAds, allMetric)
    return 'tranMetric'

if __name__ == '__main__':
    # trainThread = threading.Thread(train.run)
    logger.info("Start trainThread.")
    # trainThread.run()
    app.run(host=config.getConfig('QosMasterIP'), port=config.getConfig('QosMasterPort'))
    # trainThread.join()
    logger.info("System finished.")