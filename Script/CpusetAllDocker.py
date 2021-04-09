# 把所有docker限制在某个地方
import os

kRootPath = '/sys/fs/cgroup/cpuset/docker'
# 需要设置执行路径在根路径

cpu = '0,20'
cmdPre = 'sudo bash -c '
for i in os.listdir(kRootPath):
    if not os.path.isdir(os.path.join(kRootPath,i) ):
        continue
    cmd = cmdPre + '"' +  'echo ' + cpu + ' > ' + kRootPath + '/' + i + '/cpuset.cpus' + '"'
    os.system(cmd)