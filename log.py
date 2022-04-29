from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    Ok = 1
    Error = 2
    Critical = 3

def writeLog(logContent: str, logLevel: LogLevel):
    
    currTime = datetime.now()
    fileName = "/ImageResize/logs/" + currTime.strftime("%Y-%m-%d") + ".log"
    timeStamp = currTime.strftime("%H:%M:%S")
    f = open(fileName, "a")
    statusDict = {LogLevel.Ok: "Ok", LogLevel.Error: "Error", LogLevel.Critical: "Critical"}
    f.write("[" + timeStamp  + "][" + statusDict[logLevel] + "] " + logContent + "\n")

    f.close()

    return
    
    
