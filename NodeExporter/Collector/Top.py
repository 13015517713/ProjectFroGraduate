import subprocess
from Util import log

logger = log.getDefLogger()

# 返回一次pids数据，格式是字典，CPU:x Mem:y
def getTopByPids(pids):
    pidlist = ",".join(pids)
    cmd = "top -n 1 -p %s"%(pidlist)
    res = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=False)
    if res.returncode !=0:
        logger.error("Can't get top info.")
        return None
    toplines = res.stdout.splitlines()
    # top前五行是标题
    if len(toplines) <= 5:
        logger.error("Get top info len smarter than five lines.")
        return None
    needline = toplines[5:]
    cpu = 0
    mem = 0
    for line in needline:
        cpu += float(line.split()[8])
        mem += float(line.split()[9])
    metricData = {"cpu":str(cpu), "mem":str(mem)}
    return metricData

if __name__ == '__main__':
    # getTopByPids()
    pass