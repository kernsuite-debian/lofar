#!/usr/bin/env python3
#
# Rubidium logger implementation for CentOS7 (uses daemonize PIP package)
#
# Install/Copy this in /usr/local/bin on stations, DO NOT INSTALL IN /opt/lofar !!!!
#

import subprocess
from subprocess import Popen, PIPE
import sys
import time
from time import sleep
import termios
import resource
import os
import datetime
import glob
import logging
import logging.handlers
from daemonize import Daemonize


try:
    import codecs
except ImportError:
    codecs = None

ttMeanSpec  =   100 # +/- 100ns limit
ttMeanSs    =   100 # sample count of which mean should be lower then ttMeanSpec
ttLogLength = 86400 # Maximum number of history, 24 hours
                    # Lost lock is always resulting in wrong

logFp = None
ttHistList = []
ttMeanList = []
loHistList = []
lastOKay = False
noPPS = False
st5 = -1

workingSettings = [1280, 5, 3261, 35387, 13, 13, ['\x03', '\x1c', '\x7f', '\x15', '\x04', '\x00', '\x01', '\x00', '\x11', '\x13', '\x1a', '\x00', '\x12', '\x0f', '\x17', '\x16', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00']]

rub_logger = None
msgBuffer = []
statusFile = ""

cmdList = ['ST?', 'TT?']
advCmdList = ['AD0?', 'AD1?', 'AD2?', 'AD3?', 'AD4?', 'AD5?', 'AD6?', 'AD7?', 'AD8?', 'AD9?', 'AD10?', 'AD11?', 'AD12?', 'AD13?', 'AD14?', 'AD15?', 'AD16?', 'AD17?', 'AD18?','SD0?', 'SD1?', 'SD2?', 'SD3?', 'SD4?', 'SD5?', 'SD6?', 'SD7?','SP?','SF?','SS?','MO?','MR?','MS?','LO?','GA?','PH?','EP?','FC?','DS?', 'TO?','TS?','PS?','PL?','PT?','PF?','PI?','LM?']



def checkSettings(fp):
    curSet = termios.tcgetattr(fp)
    if curSet != workingSettings:
        cmd = 'timeout -k 5s 5s stty < /dev/rubidium'
        cf = Popen(cmd, shell = True, stdout = PIPE, stderr = PIPE)
        (result, resultErr) = cf.communicate()
        print(result.decode("UTF-8"), resultErr.decode("UTF-8"))
    else:
        return True


def callCommand(cmd):

    cmd1 = "timeout -k 5s 5s tci "
    cmd1 += cmd
    result = None
    cf = Popen(cmd1, shell = True, stdout = PIPE, stderr = PIPE)
        
    (res,resErr) = cf.communicate()
    res = res.decode("UTF-8")
    if cf.returncode != -1 and len(res)>0:
        result = res
    else:
        result = "Fail"
    return result

def statusHandler(cmd, response):
    global ttHistList, loHistList, noPPS, st5
    statusLine = "Rubidium_Status at "
    logLine = ""
    curLo = 0
    
    okay = True
        
    if cmd.find("TT?") != -1:
        if response != "Fail":
            conVal = 0
            try:
                conVal = int(response.strip())
                if conVal == -1:
                    noPPS = True
                else:
                    noPPS = False
                if conVal > 500000000 :
                    conVal = conVal - 1000000000
            except:
                conVal = -127
            ttHistList.append(abs(conVal))
        else:
            ttHistList.append(-127)
        if len(ttHistList) > ttLogLength:
            ttHistList.pop(0)
    elif cmd.find("ST?") != -1:
        if response != "Fail":
            parts = response.split(',')
            try:
                if len(parts)==6:
                    st5 = int(parts[4])
            except:
                st5 = -1
        else:
            st5 = -1
    elif cmd.find("LO?") != -1:
        resStr = response.strip()
        if resStr.find('1') != -1:
            curLo = 1
            loHistList.append(1)
        elif resStr.find('0') != -1:
            loHistList.append(0)
            curLo = 0

        if len(loHistList) > (ttLogLength // 60):
            loHistList.pop(0)

        subSet = None
        if len(ttHistList) > ttMeanSs:
            subSet =  ttHistList[ttMeanSs*-1:-1]
        else:
            subSet =  ttHistList[:]
        sum = 0
        count = 0
        for val in subSet:
            if val != -127:
                sum += val
                count += 1
        try:
            mean = float(sum) / float(count)
        except:
            mean = 2 * ttMeanSpec

        outSpec = False
        if mean > ttMeanSpec:
            outSpec = True
        outOfSpecCount = 0
        for i in ttHistList:
            if i > ttMeanSpec:
                outOfSpecCount += 1

        outOfLocCount = loHistList.count(0)
        comErrorCount = ttHistList.count(-127)

        if response == "Fail" or outSpec or curLo == 0 or st5 != 4 and st5 != 20 or noPPS:
            logLine += ": fail"
        else:
            logLine += ": okay"

        if curLo == 1 and not noPPS and (st5 == 4 or st5 == 20):
            logLine += ", rubidium lock=okay"
        else:
            logLine += ", rubidium lock=fail"

        logLine += ", pps input="
        if noPPS:
            logLine += "fail"
        else:
            logLine += "okay"
        logLine += ", status=" + str(st5)            
            
        logLine += ", communication error=" + str(comErrorCount) + " sec"
        logLine += ", outside spec +- 100 ns=" + str(outOfSpecCount) + " sec"
        logLine += ", lost lock=" + str(outOfLocCount) + " times\n"

        logTime = datetime.datetime.utcnow()
        line =  statusLine + logTime.isoformat() + logLine
#        logFp.truncate(0)
        logFp = None
        try:
            logFp = open(statusFile,"w+")
        except Exception as e:
            print("Trouble while opening a log file, details: " + e.__str__())
        logFp.write(line)
        logFp.flush()
        logFp.close()
        

def getHostName():
    cmd = 'timeout -k 1s 1s hostname -s' 
    cf = Popen(cmd, shell = True, stdout = PIPE, stderr = PIPE)
        
    (res,resErr) = cf.communicate()
    res = res.decode("UTF-8")
    if cf.returncode != -1 and len(res)>0:
        result = res.strip()
    else:
        result = "CS000"
    return result

def main():

    global ttyFp, logFp, rub_logger, statusFile

    args = sys.argv[1:]
        
    try:
        # check if port to rubidium device can be opened
        ttyFp = open("/dev/rubidium", "w+")
    except Exception as e:
        print("Trouble while opening the serial port, details: " + e.__str__())
        sys.exit()

    checkSettings(ttyFp)
    if ttyFp != None:
        ttyFp.close()

    print("running")

    first = True
    oldCur = -1
    cur = -1
    count = 0
    interval = 60
    cmdIndex = 0
    cmdStep = 4
    #Logger loop, read rubidium
    while True:
        count += 1
        #Wait loop, every second one read loop
        while cur == oldCur:
            sleep(0.01)
            cur = round(time.time())
            
        oldCur = cur
        logStr = ''
        for cmd in cmdList:
            line = callCommand(cmd)
            statusHandler(cmd,line)
            if cmd.find("TT?")!= -1:
                # Modify clock response if it returns a high value
                if line != "Fail":
                    conVal = -127
                    try:
                        conVal = int(line.strip())
                    except:
                        conVal = -127
                    if conVal > 500000000 :
                        conVal = conVal - 1000000000
                    line = str(conVal)
            logStr += cmd.strip('?') + ' ' + line.strip() + "; "
        if count >= interval or cmdIndex != 0:
            # Every 60 seconds, call all advanced commands, in groups of 4 / second
            if cmdIndex == 0:
                count = 0
            for i in range(cmdStep):
                curCmdIndex = cmdIndex + i
                if curCmdIndex < len(advCmdList):
                    cmd = advCmdList[curCmdIndex]
                    line = callCommand(cmd)
                    logStr += cmd.strip('?') + ' ' + line.strip() + "; "
                    if cmd.find("LO?")!= -1:
                        statusHandler(cmd,line)
                        
            cmdIndex += cmdStep
            if cmdIndex > len(advCmdList):
                cmdIndex = 0 
                
        printAndLog(logStr)
        if count > (round(float(len(advCmdList))/cmdStep)+1):
            sleep(0.5)
        else:
            sleep(0.2)
            
    if logFp != None:
        logFp.close()


def printAndLog(text):
    # print to log file
    global  msgBuffer
    logTime = datetime.datetime.utcnow()
    line =  logTime.isoformat() + '; ' + text
    sLine = line.strip()
    if rub_logger == None:
        msgBuffer.append(sLine)
    else:
        if len(msgBuffer)!= 0:
            for bLine in msgBuffer:
                rub_logger.info(bLine)
            msgBuffer = []
        rub_logger.info(sLine)



#Class to modify the standard python timed rotating file handler, 
# now with the specified filename structure: filename.YYmmdd
class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
  def __init__(self,dir_log):
   self.dir_log = dir_log
   filename =  self.dir_log + "." + time.strftime("%Y%m%d")
   logging.handlers.TimedRotatingFileHandler.__init__(self,filename, when='midnight', interval=1, backupCount=0, encoding=None)
   cmd = 'timeout 5s ln -fs ' + filename + ' ' + self.dir_log
   cf = Popen(cmd, shell = True, stdout = PIPE, stderr = PIPE)
   cf.communicate()
   os.chmod(filename,0o644)
   
  def doRollover(self):
   """
   TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%Y%m%d") always
   """ 
   self.stream.close()
   # get the time that this sequence started at and make it a TimeTuple
   t = self.rolloverAt - self.interval
   timeTuple = time.localtime(t)
   self.baseFilename = self.dir_log + "." + time.strftime("%Y%m%d")
    
   if self.encoding:
     self.stream = codecs.open(self.baseFilename, 'a', self.encoding)
   else:
     self.stream = open(self.baseFilename, 'a')

   cmd = 'timeout 5s ln -fs ' + self.baseFilename + ' ' + self.dir_log
   cf = Popen(cmd, shell = True, stdout = PIPE, stderr = PIPE)
   cf.communicate()
   os.chmod(self.baseFilename,0o644)
   self.rolloverAt = self.rolloverAt + self.interval


if __name__ == '__main__':

    # This construction is needed to maintain access to logfile after daemonize
    # See https://github.com/thesharp/daemonize
    hostName = getHostName()
    logFilePath = '/var/log/ntpstats/'
    statusFile = '/var/log/ntpstats/rubidium_status_' + hostName + ".log"
    logFileBase = 'rubidium_log'
    logPath  = os.path.join(logFilePath, logFileBase)

    # Set up a specific logger with our desired output level
    rub_logger = logging.getLogger('Rubidium Logger')
    rub_logger.setLevel(logging.INFO)

    # Add the log message handler to the logger 
    handler = MyTimedRotatingFileHandler(logPath)
    rub_logger.addHandler(handler)
    keep_fds = [handler.stream.fileno()]

    myname=os.path.basename(sys.argv[0])
    pidfile='/tmp/%s' % myname       # any name
    daemon = Daemonize(app=myname,pid=pidfile, action=main, keep_fds=keep_fds)
    daemon.start()
