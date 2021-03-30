import logging

__logName = "NodeExporter"
flagCreated = False

def createLogger():
    # with open("./log.out","w") as w:  # 为了清空内容
        # pass
    global __logName
    logging.basicConfig(level=logging.DEBUG,
                     format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
                     datefmt='%Y.%m.%d. %H:%M:%S')
    '''
    filename="./Log/log."
    '''
    logger = logging.getLogger(__logName)
    logger.setLevel(logging.DEBUG)       # 小于Level会被忽略 %
    flagCreated = True

def getDefLogger():
    if not flagCreated:
        createLogger()
    global __logName
    return logging.getLogger(__logName)