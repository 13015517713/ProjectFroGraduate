import json
import os
import sys
import Util.log as log

# config
kConfigPath = "/home/wcx/gitProject/projectFroGraduate/NodeExporter/config.json"
global configFileContent
global config
global logger
flagCreated = False

def init(file):
    logger = log.getDefLogger()
    global configFileContent
    global config
    configFileContent = open(file, "r")
    config = json.loads(configFileContent.read())
    flagCreated = True

def getConfig(key):
    if not flagCreated:
        init(kConfigPath)
    global configFileContent
    global config
    global logger
    if key not in config:
        logger.warning("Get key %s not found so return None."%(key) )
        return None
    return config[key]

