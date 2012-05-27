import sys
import SocketServer
import select 
import Queue
import threading
import time
from suds.client import Client, WebFault
import logging
import config
import base64
import tarfile
import gzip



authclient = None
client = None
loopClient = None
cj = None
devices = {}
exitFlag = 0

import xml.etree.ElementTree as xml

def hex2dec(s):
    """return the integer value of a hexadecimal string s"""
    return int(s[3:], 16)

def IHC_LoadProjectFile():
    global client, cj
    
    url = config.IHC_CON + '/wsdl/controller.wsdl'
    clientCtl =  Client(url)
    clientCtl.options.transport.cookiejar = cj
    clientCtl.set_options(location=config.IHC_CON + '/ws/ControllerService')    
    prj = clientCtl.service.getProjectInfo()
    noseg = clientCtl.service.getIHCProjectNumberOfSegments()
    print prj, noseg, clientCtl
    data = ''
    for i in range(noseg):
        seg = clientCtl.service.getIHCProjectSegment(i, prj['projectMajorRevision'], prj['projectMinorRevision'])
        # print i, seg
        data += seg['data']
    # print zlib.decompress(base64.b64decode(data),-1)
    file = open('project.gzip', 'wb')
    file.write(base64.b64decode(data))
    file.close()
    #print prj, noseg,
    f = gzip.open("project.gzip")
    visdata = f.read()
    f.close()
    file = open('project.vis', 'wb')
    file.write(visdata)
    file.close()
    #tar.extractall()
    #tar.close()    

def IHC_ParseProjectFile(filename):
    global devices
    tree = xml.parse(filename)
    rootElem = tree.getroot()
    groupList = rootElem.findall('groups/group')
    for group in groupList:
        gname = group.get('name')
        dataLines = group.findall('product_dataline')
        for dataLine in dataLines:
            output = dataLine.find('dataline_output') 
            if output is not None:
                devices[hex2dec(output.get('id'))] =  {'type' : 'Switch', 
                                                        'room' : gname, 
                                                        'name' : dataLine.get('name'), 
                                                        'pos'  : dataLine.get('position'), 
                                                        'value': '?'}
        airLinks = group.findall('product_airlink')
        for airLink in airLinks:
            ## print airLink, airLink.get('name'), airLink.get('position')
            dimmer = airLink.find('airlink_dimming')
            ## print "Dim", dimmer
            if dimmer is not None:
                ## print 'Dimmer', gname, dimmer.get('id'), airLink.get('position')
                devices[hex2dec(dimmer.get('id'))] =    {'type' : 'Dimmer', 
                                                         'room' : gname, 
                                                         'name' : airLink.get('name'), 
                                                         'pos'  : airLink.get('position'), 
                                                         'value': '?'}
            relay = airLink.find('airlink_relay')
            if relay is not None:
                devices[hex2dec(relay.get('id'))] =     {'type' : 'Switch', 
                                                         'room' : gname, 
                                                         'name' : airLink.get('name'), 
                                                         'pos'  : airLink.get('position'), 
                                                         'value': '?'}        
    ## print devices

def IHC_Login():
    global client, cj, loopClient
    print "Login: ",time.asctime( time.localtime(time.time()) )
    url = config.IHC_CON + '/wsdl/authentication.wsdl'
    client = Client(url)
    client.set_options(location=config.IHC_CON + '/ws/AuthenticationService')
    client.service.authenticate(config.IHC_PASS, config.IHC_USER, "treeview")
    cj = client.options.transport.cookiejar
    
    url = config.IHC_CON + '/wsdl/resourceinteraction.wsdl'
    client =  Client(url)
    client.options.transport.cookiejar = cj
    client.set_options(location=config.IHC_CON + '/ws/ResourceInteractionService')
    loopClient = client
    return client


def IHC_SetValue(device, avalue):
    val = client.factory.create('ns1:WSBooleanValue')
    val.value = avalue
    try:
        return client.service.setResourceValue(device, True, 'dataline_output', val)
    except (WebFault):
	print "Exception in SetValue"
        print WebFault
        IHC_Login()
        return IHC_SetValue(device, avalue)

def IHC_SetDimmer(device, avalue):
    val = client.factory.create('ns1:WSIntegerValue')
    
    print val
    val.integer = int(avalue)
    try:
        return client.service.setResourceValue(device, True, 'airlink_dimming', val)
    except (WebFault):
	print "Exception in SetDimmer"
        print WebFault
        IHC_Login()
        return IHC_SetDimmer(device, avalue)
        
def IHC_EnableNotifications(devices):
    try:
        return client.service.enableRuntimeValueNotifications(devices)        
    except (WebFault):
	print "Exception in EnableNotify"
	print WebFault
        IHC_Login()
        return IHC_EnableNotifications(devices)

def IHC_waitForNotifications(wait, devices):
    print time.asctime( time.localtime(time.time()) )
    print wait
    print client.options.transport.cookiejar
    try:
        return client.service.waitForResourceValueChanges(wait)        
    except (WebFault):
	print "Exception in WaitForNotify"
        IHC_Login()
        IHC_EnableNotifications(devices)
        return IHC_waitForNotifications(wait, devices)
    
class waitForNot(threading.Thread):    
    global devices
    global exitFlag
    global queueLock, workQueue
    
    def __init__(self, wfile):
        self.wfile = wfile
        threading.Thread.__init__(self)
        
    def run(self):
         IHC_EnableNotifications(devices.keys())
         while 1:
             val = IHC_waitForNotifications(config.EVENTWAIT, devices.keys())
             response = ''
             if val is not None:
                 for res in val:
                     if res is not None:
                         if devices[res.resourceID]['type'] == 'Dimmer':
                             value = res.value.integer
                         else:
                             value = res.value.value
                         if devices[res.resourceID]['value'] <> value:
                              response += 'updatevalue,%d,%s\n' %(res.resourceID, value)
                              devices[res.resourceID]['value'] = value
             ##self.wfile.write('looping\n\r')
             if len(response):
                 self.wfile.write(response)
#                 queueLock.acquire()
#                 workQueue.put(response)
#                 queueLock.release()
                 print "Quede up: " + response
             if exitFlag:
                 self.exit()    
               
class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        global devices
        global exitFlag
        global queueLock, workQueue
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        waitFor = waitForNot(self.wfile)
        
        self.stopflag = False
        while not self.stopflag:
#            queueLock.acquire()
#            if not workQueue.empty():
#                data = workQueue.get()
#                queueLock.release()
#                print "Response: " + data
#                self.wfile.write(data)
#            else:
#                queueLock.release()
#                
#            ready_to_read, ready_to_write, in_error = select.select([self.rfile], [], [], None)
#                
#            if len(ready_to_read) == 1 and ready_to_read[0] == self.rfile:    
            line = self.rfile.readline().strip()
            """Process a command"""
            args = line.split(' ')
            command = args[0].lower()
            args = args[1:]
            print "Command: " + command
            if command == 'hello':
                self.wfile.write('HELLO TO YOU TO!\n\r')
                ##return COMMAND_HELLO
            elif command == 'query':
		if waitFor.is_alive():
		    exitFlag = 1	
                for address, device in devices.iteritems():
                    self.wfile.write((u'device,%d,%s,%s/%s/%s\n' % (address, device['type'], device['room'], device['pos'], device['name'])).encode('utf-8'))
                self.wfile.write((u'deviceend\n'))    
            elif command == 'setvalue':
                if len(args) == 2:
                    self.wfile.write(IHC_SetValue(args[0], args[1]))
                else:
                    self.wfile.write('Argument error\n')
	    elif command == 'setdimmer':
                if len(args) == 2:
                    self.wfile.write(IHC_SetDimmer(args[0], args[1]))
                else:
                    self.wfile.write('Argument error\n')
            elif command == 'wait':
	        if waitFor.is_alive():
		    exitFlag = 1	
                waitFor.start()
                #waitFor.run()
                print "wait for started"   
                ##IHC_EnableNotifications(devices.keys())
                ##while 1:
#                ##    val = IHC_waitForNotifications(config.EVENTWAIT, devices.keys())
#                    if val is not None:
#                        for res in val:
#                            if res is not None:
#                                 if devices[res.resourceID]['type'] == 'Dimmer':
#                                     value = res.value.integer
#                                 else:
#                                     value = res.value.value
#                                 if devices[res.resourceID]['value'] <> value:
#                                      self.wfile.write('updatevalue: %d %s\n' %(res.resourceID, value))
#                                      devices[res.resourceID]['value'] = value
#                    self.wfile.write('looping\n\r')           
            elif command == 'quit':
                exitFlag = 1
                self.wfile.write('OK, SEE YOU LATER\n')
                self.stopflag = True
		exit()
            else:
                self.wfile.write('Unknown command: "%s"\n' % command)

	def finish(self):
	    exit()	            

if __name__ == "__main__":
    
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((config.HOST, config.PORT), MyTCPHandler)
    
    
    
    
    logging.basicConfig(level=config.LOGLEVEL)
    
    logging.getLogger('suds.client').setLevel(logging.ERROR)
    
    client = IHC_Login()
    IHC_LoadProjectFile()
    IHC_ParseProjectFile('project.vis')
       
    queueLock = threading.Lock()
    workQueue = Queue.Queue(10)
        
    ##print client
    ##print client.service.enableRuntimeValueNotifications([379995])
    
    ##print time.asctime( time.localtime(time.time()) )
    ##print client.service.waitForResourceValueChanges(300)
    ##print time.asctime( time.localtime(time.time()) )
    
    ##val = client.factory.create('ns1:WSBooleanValue')
    ##print val
    ##val.value = False
    ##print val
    ##print client.service.setResourceValue(7643486, True, 'dataline_output', val)


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "Starting server"
    server.serve_forever()
