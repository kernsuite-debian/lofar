#!/usr/bin/python3 -B
## P.Donker ASTRON februari 2011
## station EC lib module

import socket
import struct
import time

def getIP():
    # get ip-adres of LCU
    local_host = socket.gethostbyname(socket.gethostname())
    ip = local_host.split('.')
    if ip[0] == '10' and (ip[1] == '151' or ip[1] == '209'):
        # if LCU adress make it EC adress
        return(local_host[:local_host.rfind('.')+1]+'3')
    return(None)

class EC:
    # cmdIDs from TCP PROTOCOL ec-controller
    EC_NONE             = 0
    EC_STATUS           = 1
    EC_CTRL_TEMP        = 3
    EC_VERSION          = 5
    EC_STATION_INFO     = 6
    EC_SET_HEATER       = 17
    EC_SET_48           = 20
    EC_RESET_48         = 22
    EC_SET_LCU          = 25
    EC_RESET_LCU        = 27
    EC_RESET_TRIP       = 28
    SET_OBSERVING       = 120

    PWR_OFF      = 0
    PWR_ON       = 1
    P_48         = 0
    P_LCU        = 1
    P_ALL        = 2

    printToScreen = False
    host = None
    station = None
    port = 10000
    sck = None
    logger = False
    info = ''
    version = 0
    versionstr = 'V-.-.-'

    def __init__(self, addr='0.0.0.0'):
        self.host = addr
        try:
            (hostname,a,b) = socket.gethostbyaddr(addr)
            self.station = hostname.split('.')[0]
        except:
            self.station = 'Unknown'

    def setInfo(self, info):
        self.info = info
        if self.printToScreen:
            print((self.info))
            self.info = ''
        else: self.info += '\n'
        return

    def addInfo(self, info):
        self.info += info
        if self.printToScreen:
            print((self.info))
            self.info = ''
        else: self.info += '\n'
        return

    def printInfo(self, state=True):
        self.printToScreen = state
        return

    #---------------------------------------
    def connectToHost(self):
        self.setInfo("connecting to %s on port %d" %(self.host, self.port))
        connected = False

        try:
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            self.sck.close()
            return(connected)

        try:
            self.sck.settimeout(3.0)
            self.sck.connect((self.host, self.port))
            connected = True
            time.sleep(0.5)
            self.getVersion()
            if self.version > 200:
                self.getStationInfo()
        except socket.error:
            self.sck.close()
        return(connected)

    #---------------------------------------
    def disconnectHost(self):
        self.setInfo("closing %s" %(self.host))
        self.sck.close()
        time.sleep(0.5)
        return

    #---------------------------------------
    def sendCmd(self, cmdId=0, cab=-1, value=0):
        if (cmdId == self.EC_NONE):
            return (false)
        try:
            cmd = struct.pack('hhh', cmdId, cab, int(value))
            self.sck.send(cmd)
        except socket.error:
            self.setInfo("socket error, try to reconnect")
            self.disconnectHost()
            time.sleep(10.0)
            self.connectToHost()
        return
    #---------------------------------------
    def recvAck(self):
        socketError = False
        try:
            self.sck.settimeout(1.0)
            data = self.sck.recv(6)
        except socket.error:
            socketError = True
            self.setInfo("socket error, try to reconnect")
            #self.disconnectHost()
            #self.connectToHost()
        if socketError:
            return(0,0,[])

        header = struct.unpack('hhh', data)
        cmdId = header[0]
        status = header[1]
        PLSize = header[2]
        if (PLSize > 0):
            data = self.sck.recv(PLSize)
            fmt = 'h' * (PLSize // 2)
            PL = struct.unpack(fmt, data)
        else:
            PL = []
        return (cmdId, status, PL)
    #---------------------------------------
    def setPower(self, pwr=P_ALL, state=PWR_ON):
        if ((pwr == self.P_48) or (pwr == self.P_ALL)):
            self.sendCmd(self.EC_SET_48, 0, state)
            (cmdId, status, PL) = self.recvAck()
            self.setInfo('Power Set 48V to %d' %(state))
        if ((pwr == self.P_LCU) or (pwr == self.P_ALL)):
            self.sendCmd(self.EC_SET_LCU, 0, state)
            (cmdId, status, PL) = self.recvAck()
            self.setInfo('Power Set LCU to %d' %(state))
        return(self.info)
    #---------------------------------------
    def resetPower(self, pwr=P_ALL):
        if ((pwr == self.P_48) or (pwr == self.P_ALL)):
            self.sendCmd(self.EC_RESET_48, 0, 0)
            (cmdId, status, PL) = self.recvAck()
            self.setInfo('PowerReset 48V')
        if ((pwr == self.P_LCU) or (pwr == self.P_ALL)):
            self.sendCmd(self.EC_RESET_LCU, 0, 0)
            (cmdId, status, PL) = self.recvAck()
            self.setInfo('PowerReset LCU')
        return(self.info)
    #---------------------------------------
    def resetTrip(self):
        self.sendCmd(self.EC_RESET_TRIP, -1, 0)
        (cmdId, status, PL) = self.recvAck()
        self.setInfo('Reset Trip System')
        return(self.info)
    #---------------------------------------
    def setHeater(self, mode=0):
        self.sendCmd(self.EC_SET_HEATER, -1, mode)
        (cmdId, status, payload) = self.recvAck()

        if (mode == self.MODE_ON): self.setInfo('heater is turned ON')
        if (mode == self.MODE_OFF): self.setInfo('heater is turned OFF')
        if (mode == self.MODE_AUTO): self.setInfo('heater set to AUTO')

    #---------------------------------------
    def getVersion(self):
        self.sendCmd(self.EC_VERSION)
        (cmdId, status, PL) = self.recvAck()
        try:
            version = int((PL[0]*100)+(PL[1]*10)+PL[2])
            versionstr = 'V%d.%d.%d' %(PL)
            self.version = version
            self.versionstr = versionstr
            self.setInfo('EC software version %d.%d.%d' %(PL))
        except:
            version = 0
            versionstr = 'V0.0.0'
            self.version = version
            self.versionstr = versionstr
            self.setInfo('EC software version 0.0.0')

        return version, versionstr

    def getStationInfo(self):
        stationType = ('Unknown','NAA','Unknown','LOFAR NL','LOFAR IS','Unknown')
        wxt520Text = ('not available','available')
        self.sendCmd(self.EC_STATION_INFO)
        (cmdId, status, PL) = self.recvAck()

        type = int(PL[0])
        wxt520 = int(PL[1])
        self.stationtype = type
        self.wxt520present = wxt520
        self.setInfo('station type: %s,   wxt520: %s' %\
            (stationType[type], wxt520Text[wxt520]))
        return type, wxt520

    #---------------------------------------
    def getStatusData(self):
        self.sendCmd(self.EC_STATUS)
        (cmdId, status, PL2) = self.recvAck()
        return PL2

    def getStatus(self):
        if self.stationtype == 3:
            self.statusNL()
            return()
        if self.stationtype == 4:
            self.statusIS()
            return()
        self.setInfo("Unsupported station type")

    def statusNL(self):
        ec_mode = ('OFF','ON','AUTO','MANUAL','STARTUP','AUTO-SEEK','ABSENT','TEST')
        fan = ('.  .  .  .','.  .  .  .','.  2  .  .','1  2  .  .',\
               '.  .  3  .','.  .  .  .','.  2  3  .','1  2  3  .',\
               '.  .  .  .','.  .  .  .','.  .  .  .','.  .  .  .',\
               '.  .  3  4','.  .  .  .','.  2  3  4','1  2  3  4')

        door = ('CLOSED','FRONT_OPEN','BACK_OPEN','ALL_OPEN')
        fanstate = ('BAD | BAD ','GOOD| BAD ','BAD | GOOD','GOOD| GOOD')
        fanestate= ('OFF | OFF ','ON  | OFF ','OFF | ON  ','ON  | ON  ')
        onoff = ('OFF','ON')
        badok = ('N.A.','OK')

        # get information from EC
        self.sendCmd(self.EC_CTRL_TEMP)
        (cmdId, status, PL1) = self.recvAck()
        self.sendCmd(self.EC_STATUS)
        (cmdId, status, PL2) = self.recvAck()
        if len(PL1) == 0 or len(PL2) == 0: return
        # fill lines with data
        lines = []

        lines.append('            |')
        lines.append('mode        |')
        lines.append('status      |')
        lines.append('set point   |')
        lines.append('temperature |')
        lines.append('humidity    |')
        lines.append('fans        |')
        lines.append('fane        |')
        lines.append('fans state  |')
        lines.append('doors       |')
        lines.append('heater      |')
        cabs = [0,1,3]
        for nCab in range(3):
            cab = cabs[nCab]
            lines[0] += '  cabinet %1d |' %(cab)
            lines[1] += '%11s |' %(ec_mode[PL2[(cab*7)]])
            lines[2] += '     %#06x |' %(PL2[(cab*7)+1])
            lines[3] += '%11.2f |' %(PL1[cab]/100.)
            lines[4] += '%11.2f |' %(PL2[(cab*7)+2]/100.)
            lines[5] += '%11.2f |' %(PL2[(cab*7)+3]/100.)
            lines[6] += '%11s |' %(fan[(PL2[(cab*7)+4]&0x0f)])
            lines[7] += '%11s |' %(fanestate[(PL2[(cab*7)+4]>>4)&0x3])
            lines[8] += '%11s |' %(fanstate[(PL2[(cab*7)+4]>>6)&0x3])
            lines[9] += '%11s |' %(door[(PL2[(cab*7)+5]&0x03)])
            if (cab != 3):
                lines[10] += '%11s |' %('none')
            else:
                lines[10] += '%11s |' %(onoff[PL2[(cab*7)+6]])

        i = 28
        lines.append('power 48V state  = %s' %(onoff[(PL2[i] & 1)]))
        lines.append('power LCU state  = %s' %(onoff[(PL2[i] >> 1)]))
        lines.append('lightning state  = %s' %(badok[(PL2[i+1] & 1)]))

        # print lines to screen or file, see printInfo
        info = 'status %s (%s)     %s ' %(self.station, self.versionstr, time.asctime())
        self.setInfo('-' * len(info))
        self.addInfo(info)
        self.addInfo('-' * len(info))

        for line in lines:
            self.addInfo(line)

    def statusIS(self):
        onoff = ('OFF','ON')
        badok = ('N.A.','OK')

        # get information from EC
        self.sendCmd(self.EC_CTRL_TEMP)
        (cmdId, status, PL1) = self.recvAck()
        self.sendCmd(self.EC_STATUS)
        (cmdId, status, PL2) = self.recvAck()
        if len(PL1) == 0 or len(PL2) == 0: return
        # fill lines with data
        lines = []
        lines.append('temperature      = %5.2f' %(PL2[2]/100.))
        lines.append('humidity         = %5.2f' %(PL2[3]/100.))
        lines.append('heater state     = %s' %(onoff[PL2[(3*7)+6]]))
        lines.append('power 48V state  = %s' %(onoff[(PL2[28] & 1)]))
        lines.append('power LCU state  = %s' %(onoff[(PL2[28] >> 1) & 1]))
        lines.append('lightning state  = %s' %(badok[(PL2[29] & 1)]))

        # print lines to screen or file, see printInfo
        info1 = ' %s      (EC %s)' %(self.station, self.versionstr)
        info2 = ' %s ' %(time.asctime())
        self.setInfo('-' * len(info2))
        self.addInfo(info1)
        self.addInfo(info2)
        self.addInfo('-' * len(info2))
        for line in lines:
            self.addInfo(line)

    #---------------------------------------
    def getPowerStatus(self):
        state = ('OFF','ON')
        # get information from EC
        self.sendCmd(self.EC_STATUS)
        (cmdId, status, PL) = self.recvAck()
        powerstate = PL[28] & 1
        self.addInfo('Power: 48V = %s, LCU = %s' %(state[(PL[28] & 1)], state[(PL[28] >> 1)]))
        return powerstate

    #---------------------------------------
    def getTripStatus(self):
        # get information from EC
        self.sendCmd(self.EC_STATUS)
        (cmdId, status, PL) = self.recvAck()
        state = False
        if (PL[1] & 0x1000):
            self.addInfo('trip in cabinet 0')
            state = True
        if (PL[8] & 0x1000):
            self.addInfo('trip in cabinet 1')
            state = True
        if (PL[22] & 0x1000):
            self.addInfo('trip in cabinet 3')
            state = True

        if (PL[1] & 0x6000):
            self.addInfo('warning in cabinet 0')
            state = True
        if (PL[8] & 0x6000):
            self.addInfo('warning in cabinet 1')
            state = True
        if (PL[22] & 0x6000):
            self.addInfo('warning in cabinet 3')
            state = True

        if (state == False):
            self.addInfo('NO trips available')
        return(state)

    #---------------------------------------
    ## set observing active(1) or not active(0)
    def setObserving(self, state=0):
        self.sendCmd(self.SET_OBSERVING, -1, state)
        (cmdId, status, PL) = self.recvAck()
        self.setInfo('SetObserving to %d' %(state))
        return(self.info)
