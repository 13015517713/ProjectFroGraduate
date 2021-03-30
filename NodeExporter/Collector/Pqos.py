import sys
import subprocess

'''
Pqos旨为拿到某个时刻llc、mbl、mbr等以及占用的cores
'''

class PqosTool:
    def __init__(self):
        pass

    def getMetricByPids(self, pidlist, sleepTime=5):
        cmd = "sudo pqos -I -p "
        pass

    def getMetricByGroup(self, group, sleepTime=5):
        pass

if __name__ == '__main__':
    pass