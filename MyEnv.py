import os

envDic = {}
HOME = os.environ.get("HOME")
dicPath = "%s/.myPythonEnv" % HOME
initFlag = False

def setMyPythonEnv(key, value):
    global initFlag
    global dicPath
    if not initFlag:
        loadDic(dicPath)
    envDic[key] = value
    saveDic(dicPath)
def getMyPythonEnv(key):
    global initFlag
    global dicPath
    if not initFlag:
        loadDic(dicPath)
    return envDic.get(key)

def loadDic(dicPath):
    global envDic    
    fp = open(dicPath, "a+")
    envList = fp.readlines()
    '''
    repeatCount 2
    '''
    for line in envList:
        element = line.split(":")
        envDic[element[0]] = element[1].strip()

    fp.close()

def saveDic(dicPath):
    global envDic
    fp = open(dicPath, "w+")
    for key, value in envDic.items():
        fp.write(key)
        fp.write(":")
        fp.write(value)
        fp.write("\n")
        fp.flush()
    fp.close()

def getArg(key, returnType):
    lastArg = getMyPythonEnv(key)
    arg = raw_input(("%s(%s): " % (key, lastArg)))
    if arg == "":
        arg = lastArg
    else:
        setMyPythonEnv(key, arg)
    if returnType == "int":
        return int(arg)
    elif returnType == "str":
        return arg
