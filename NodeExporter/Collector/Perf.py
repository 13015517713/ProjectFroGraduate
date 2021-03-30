# 一次性执行，输入Pids然后得到对应的指标
import subprocess
import sys
sys.path.append("/home/wcx/gitProject/projectFroGraduate/NodeExporter/") # forSinglefileDebug
# print(sys.path)
from Util import log
logger = log.getDefLogger()

# 配置需要采取的指标，包含静态指标和动态指标
# 学长默认采样4s

allTar = ["instructions","cycles","cpu/event=0xd0,umask=0x83/","cache-misses","cpu/event=0xd0,umask=0x21/","cpu/event=0xc7,umask=3/","cpu/event=0xc4,umask=0x0/","cpu/event=0xd1,umask=0x8/","cpu/event=0xd1,umask=0x10/","cpu/event=0xa2,umask=0x8/","cpu/event=0xc5,umask=0x4/","cpu/event=0xc3,umask=0x1/",\
          "cpu/event=0x9c,umask=0x01/","cpu/event=0x0e,umask=0x01/","cpu/event=0xc2,umask=0x02/","cpu/event=0x0d,umask=0x03/"]
perfPath = 'perf'
fromEvent = {
        "cpu/event=0xd0,umask=0x83/" : "loads_and_stores",
        "cpu/event=0x0e,umask=0x01/" : "uops_issued.any",
        "cpu/event=0x9c,umask=0x01/" : "idq_uops_not_delivered.core", 
        "cpu/event=0xc2,umask=0x02/" : "uops_retired.retire_slots", 
        "cpu/event=0x0d,umask=0x03/" : "int_misc.recovery_cycles", # this
        "cpu/event=0xc7,umask=3/" : "fp_uops",
        "cpu/event=0xc4,umask=0x0/" : "branch", # this
        "cpu/event=0xd0,umask=0x21/" : "lock_loads",
        "cpu/event=0xd1,umask=0x8/" : "l1_misses", # this
        "cpu/event=0xd1,umask=0x10/" : "l2_misses", # this
        "cpu/event=0xa2,umask=0x8/" : "stall_sb",
        "cpu/event=0xc5,umask=0x4/" : "branch_misp",
        "cpu/event=0xc3,umask=0x1/" : "machine_clear"
}
toEvent = {
     "loads_and_stores":"cpu/event=0xd0,umask=0x83/",
     "uops_issued.any": "cpu/event=0x0e,umask=0x01/",
     "idq_uops_not_delivered.core":"cpu/event=0x9c,umask=0x01/",
     "uops_retired.retire_slots":"cpu/event=0xc2,umask=0x02/",
     "int_misc.recovery_cycles":"cpu/event=0x0d,umask=0x03/",
    "fp_uops":        "cpu/event=0xc7,umask=3/",
    "branch":           "cpu/event=0xc4,umask=0x0/" ,
     "lock_loads":      "cpu/event=0xd0,umask=0x21/",
    "l1_misses":      "cpu/event=0xd1,umask=0x8/" ,
     "l2_misses":       "cpu/event=0xd1,umask=0x10/",
    "stall_sb":       "cpu/event=0xa2,umask=0x8/" ,
    "branch_misp":      "cpu/event=0xc5,umask=0x4/", 
    "machine_clear":     "cpu/event=0xc3,umask=0x1/" 
}

class PerfTool:
    def __init__(self):
        pass
    def getMetricByPids(self, pidlist, sleepTime=5): # 直接返回带指标结构的字典结构即可
        cmd = 'sudo perf stat -x "|" -e '
        allMetric = ",".join(allTar )
        cmd += allMetric
        pids = ",".join([str(pid) for pid in pidlist] )
        cmd += " -p " + pids
        cmd += " sleep %f"%(float(sleepTime) )
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res.returncode != 0:
            return None
        metricInfo = {}
        tinfo = str(res.stdout, encoding='utf-8').strip().split('\n')
        '''
        print('----------------------------------------------------')
        print(res.stdout)
        print('-----------------------------------------------------------')
        '''
        for i in range(len(allTar) ):
            metric = allTar[i]
            if metric in fromEvent:
                metric = fromEvent[metric]
            infoline = tinfo[i].strip().split('|')
            # 可能会出现||连在一起的状况
            if infoline[1] == '':
                del infoline[1]
            val = infoline[0]
            if val.find('not counted') != -1:
                logger.fatal("Metric %s can't be count so set 0."%(metric) )
                val = 0
            if infoline[1] == 'instructions':
                metricInfo["ipc"] = float(infoline[4]) if val.find('not counted') == -1 else 0
            metricInfo[metric] = float(val)  
        return metricInfo

    def getMetricByGroup(self, group, sleepTime=5): # 直接返回指标组
        cmd = "sudo perf stat -e "
        allMetric = ",".join(allTar)
        cmd += allMetric
        cmd += " -G " + group
        cmd += " sleep %f"%(float(sleepTime) )
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res.returncode != 0:
            return None
        metricInfo = {}
        tinfo = str(res.stdout, encoding='utf-8').strip().split('\n')
        for i in range(len(allTar) ):
            metric = allTar[i]
            infoline = tinfo[i].strip().split('|')
            # 可能会出现||连在一起的状况
            if infoline[1] == '':
                del infoline[1]
            val = infoline[0]
            if val.find('not counted') != -1:
                logger.fatal("Metric %s can't be count so set 0."%(metric) )
                val = 0
            if infoline[1] == 'instructions':
                metricInfo["ipc"] = float(infoline[4]) if val.find('not counted') != -1 else 0
            metricInfo[metric] = float(val)  
        return metricInfo


if __name__ == "__main__":
    Pf = PerfTool()
    pids = [4773,4858,28277]
    # t = [str(i) for i in pids]
    Pf.getMetricByPids(pids)