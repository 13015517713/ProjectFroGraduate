# Todo:
# 1.用flask框架实现注册，接收Kubernetes的注册信息，然后注册成功
# 2.
from Util import log,config,httpbin as ht
import rootDir
import json
import time
from flask import Flask,request
from Collector import Perf
from Collector import Pqos

# log
logger = log.getDefLogger()

# config
CgroupRootDir = rootDir.RootDir(config.getConfig("rootDir") ) # Docker or Pod

# 1.更新RootDir目录，对改变的Docker/Pod注册销毁等
# 2.对当前存在的Docker/Pod采集指标，主要包括LLC和Perf采集到的一系列指标
def mainloop():
    Url = config.getConfig("QosMasterUrl")
    Pf = Perf.PerfTool()
    Pq = Pqos.PqosTool()
    logger.info("Start to run mainLoop.")
    timeSleep = float(config.getConfig("timeSleep"))
    # res = CgroupRootDir.load()  # 更新rootdir目录，添加的就注册
    while True:
        lenUpdate = CgroupRootDir.load()
        # 1.1 发注册请求
        added = CgroupRootDir.popAlladded()
        logger.info("Docker updates add %d dockers."%(len(added)) )
        for docker in added:
            if rootDir.isNeed(docker.getName()) == False:
                logger.debug("Docker name=%s can't register."%(docker.getName()) )
                continue
            tranInfo = {'dockername':docker.getName(), 'dockerid':docker.getId()}
            ht.sendHttpByGet(Url+'register', data=tranInfo)
        
        # 1.2 发删除请求
        subed = CgroupRootDir.popAllsubed()
        logger.info("Docker updates sub %d dockers."%(len(subed)) )
        for docker in subed:
            if rootDir.isNeed(docker.getName()) == False:
                logger.debug("Docker name=%s can't loggout."%(docker.getName()) )
                continue
            tranInfo = {'dockername':docker.getName(), 'dockerid':docker.getId()}
            ht.sendHttpByGet(Url+'logout', data=tranInfo)
        
        # 2.1 Perf采集指标
        # 传Pid然后得到此刻的数据，和docker对应起来，然后发过去。
        dockers = CgroupRootDir.getAllDocker()
        tranInfo = []
        for docker in dockers:
            if rootDir.isNeed(docker.getName()) == False:
                continue
            perfInfo = Pf.getMetricByGroup(docker.getGroup()) 
            tInfo = {"dockerName":docker.getName(),
                        "dockerId":docker.getId(),
                        "dockerMetric":perfInfo}
            tranInfo.append(tInfo)
        # 发送指标，这里是统一发的，不过目前指标不是统一截取的
        ht.sendHttpByPost(Url + 'tranMetric', "data", json.dumps(tranInfo))

        # 2.2 Pqos采集指标，目前先不需要
        for docker in dockers:
            # Pq.getMetricByPids(docker.getPids())
            pass
    
        # time.sleep(timeSleep)
        

if __name__ == '__main__':
    mainloop()
    