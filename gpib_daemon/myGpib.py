#!/usr/bin/env python
import gpib

RQS = (1<<11)
SRQ = (1<<12)
TIMO = (1<<14)


ibsta_dic = {0 : ('DCAS', 'device clear command'),
             1 : ('DTAS', 'device trigger command'),
             2 : ('LACS', 'board is listener'),
             3 : ('TACS', 'board is talker'),
             4 : ('ATN', 'ATN line asserted'),
             5 : ('CIC', 'board is Controller-in-Charge'),
             6 : ('REM', 'board in remote state'),
             7 : ('LOK', 'board in lockout state'),
             8 : ('CMPL', 'I/O Complete'),
             9 : ('EVENT', 'Clear, trigger or interface event'),
             10 : ('SPOLL', 'board is serial polled'),
             11 : ('RQS', 'device has requested service'),
             12 : ('SRQI', 'board asserting SRQ line'),
             13 : ('END', 'I/O operation ended with EOI'),
             14 : ('TIMO', 'I/O or ibwait timed out'),
             15 : ('ERR', 'Error')
             }


class Gpib:
    def __init__(self, name='gpib0', eot=True):
        self.id = gpib.find(name)
        if eot:
            self.eot = True
        else:
            self.eot = False

    def write(self,text):
        if self.eot:
            text += "\n"
        gpib.write(self.id, text)
        
    def writebin(self,text,len):
        gpib.writebin(self.id,text,len)
        

    def read(self,len=512):
        self.res = gpib.read(self.id,len)
        return self.res.replace('\n','').replace('\r','')
    
    def ask(self, text,readlen=512):
        "Send a write and then do a read"
        self.write(text)
        return self.read(len=readlen)

    def readbin(self,len=512):
        self.res = gpib.readbin(self.id,len)
        return self.res

    def clear(self):
        gpib.clear(self.id)
        
    def wait(self,mask):
        gpib.wait(self.id,mask)
	
    def rsp(self):
        self.spb = gpib.rsp(self.id)
        return self.spb

    def trigger(self):
        gpib.trg(self.id)
        
    def ren(self,val):
        gpib.ren(self.id,val)

    def ibsta(self):
        self.res = gpib.ibsta()
        return self.res

    def ibcnt(self):
        self.res = gpib.ibcnt()
        return self.res

    def tmo(self,value):
        return gpib.tmo(self.id,value)

    def status(self):
        stat = gpib.ibsta()
        statvals = {}
        for key in ibsta_dic:
            if stat & (1 << key): statvals[ibsta_dic[key][0]] = ibsta_dic[key][1]
        return statvals

