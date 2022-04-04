#!/usr/bin/env python3

import sys
import time 
from  TeslaInfo import tesla_info
from TeslaPWSetupNode import teslaPWSetupNode
from TeslaPWStatusNode import teslaPWStatusNode
from TeslaPWSolarNode import teslaPWSolarNode
from TeslaPWGenNode import teslaPWGenNode

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)

class TeslaPWController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(TeslaPWController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot

        logging.info('_init_ Tesla Power Wall Controller')
        self.ISYforced = False
        self.name = 'Tesla PowerWall Info'
        self.primary = primary
        self.address = address
        self.cloudAccess = False
        self.localAccess = False
        self.initialized = False
        self.Rtoken = None
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
       
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))
        self.hb = 0
        
        self.nodeDefineDone = False
        self.longPollCountMissed = 0

        logging.debug('Controller init DONE')
        
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.setDriver('ST', 1, True, True)
        logging.debug('finish Init ')

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
       
        logging.debug('start')
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        # Wait for things to initialize....

        while not self.initialized:
            time.sleep(1)

        if self.cloudAccess or self.localAccessl:
            self.tesla_initialize(self.local_email, self.local_password, self.local_ip, self.Rtoken)
        else:
            self.poly.Notices['cfg'] = 'Tesla PowerWall NS needs configuration.'
        # Poll for current values (and update drivers)
        self.TPW.pollSystemData('all')          
        self.updateISYdrivers('all')
        self.TPW.systemReady = True
   


    '''
    This may be called multiple times with different settings as the user
    could be enabling or disabling the various types of access.  So if the
    user changes something, we want to re-initialize.
    '''
    def tesla_initialize(self, local_email, local_password, local_ip, Rtoken):
        logging.debug('starting Login process')
        try:
            #del self.Parameters['REFRESH_TOKEN']
            self.TPW = tesla_info(self.name, self.address, self.localAccess, self.cloudAccess)
            if self.localAccess:
                logging.debug('Attempting to log in via local auth')
                try:
                    self.localAccessUp  = self.TPW.loginLocal(local_email, local_password, local_ip)
                except:
                    logging.error('local authenticated failed.')
                    self.localAccess = False

            if self.cloudAccess:
                logging.debug('Attempting to log in via cloud auth')
                #self.TPW.loginCloud(cloud_email, cloud_password)
                self.cloudAcccessUp = self.TPW.teslaCloudConnect(Rtoken)
                logging.debug('finiahed login procedures' )

            if not self.localAccess and not self.cloudAccess:
                logging.error('Configuration invalid, initialization aborted.')
                self.poly.Notices['err'] = 'Configuration is not valid, please update configuration.'
                return
         
            self.TPW.teslaInitializeData()
            '''
            node addresses:
               setup node:            pwsetup 'Control Parameters'
               main status node:      pwstatus 'Power Wall Status'
               generator status node: genstatus 'Generator Status'
               solar status node:     solarstatus 'Solar Status'
            '''
            
            logging.info('Creating Nodes')
            if not self.poly.getNode('pwstatus'):
                node = teslaPWStatusNode(self.poly, self.address, 'pwstatus', 'Power Wall Status', self.TPW)
                self.poly.addNode(node)
                self.wait_for_node_done()
            if self.TPW.solarInstalled:
                if not self.poly.getNode('solarstatus'):
                    node = teslaPWSolarNode(self.poly, self.address, 'solarstatus', 'Solar Status', self.TPW)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
            else:
                self.poly.delNode('solarstatus')

            if self.TPW.generatorInstalled:
                if not self.poly.getNode('genstatus'):
                    node = teslaPWGenNode(self.poly, self.address, 'genstatus', 'Generator Status', self.TPW)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
            else:
                self.poly.delNode('genstatus')

            if self.cloudAccess:
                if not self.poly.getNode('pwsetup'):
                    node = teslaPWSetupNode(self.poly, self.address, 'pwsetup', 'Control Parameters', self.TPW)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
            else:
                self.poly.delNode('pwsetup')

            logging.debug('Node installation complete')
            self.nodeDefineDone = True
            self.initialized = True

        except Exception as e:
            logging.error('Exception Controller start: '+ str(e))
            logging.info('Did not connect to power wall')

        logging.debug ('Controller - initialization done')

    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))

    def handleParams (self, customParam ):
        logging.debug('handleParams')
        supportParams = ['LOCAL_USER_EMAIL','LOCAL_USER_PASSWORD','LOCAL_IP_ADDRESS', 'REFRESH_TOKEN'   ]
        self.Parameters.load(customParam)

        logging.debug('handleParams load')
        #logging.debug(self.Parameters)  ### TEMP
        self.poly.Notices.clear()
        cloud_valid = False
        local_valid = False
        self.localAccess = False
        self.cloudAccess = False
        for param in customParam:
            if param not in supportParams:
                del self.Parameters[param]
                logging.debug ('erasing key: ' + str(param))


        if 'LOCAL_USER_EMAIL' in customParam:
            self.local_email = customParam['LOCAL_USER_EMAIL']
        else:
            self.poly.Notices['lu'] = 'Missing Local User Email parameter'
            self.local_email = ''
            #self.Parameters['LOCAL_USER_EMAIL']  = local_email
            
        if 'LOCAL_USER_PASSWORD' in customParam:
            self.local_password = customParam['LOCAL_USER_PASSWORD']
        else:
            self.poly.Notices['lp'] = 'Missing Local User Password parameter'
            self.local_password = ''
            #self.Parameters['LOCAL_USER_PASSWORD']  = local_password

        if  'LOCAL_IP_ADDRESS' in customParam:
            self.local_ip = self.Parameters['LOCAL_IP_ADDRESS']
        else:
            self.poly.Notices['ip'] = 'Missing Local IP Address parameter'
            self.local_ip = ''
            #self.Parameters['LOCAL_IP_ADDRESS']  = local_ip


        if 'REFRESH_TOKEN' in customParam:
            self.Rtoken = self.Parameters['REFRESH_TOKEN']
            if self.Rtoken  == '':
                self.poly.Notices['ct'] = 'Missing Cloud Refresh Token'
            else:
                if 'ct' in self.poly.Notices:
                    self.poly.Notices.delete('ct')      
            '''
            cloud_token = customParam['REFRESH_TOKEN']
            if cloud_token != '':
                if (os.path.exists('./inputToken.txt')):
                    dataFile = open('./inputToken.txt', 'r')
                    tmpToken = dataFile.read()
                    dataFile.close()
                    if tmpToken != cloud_token:
                        dataFile = open('./inputToken.txt', 'w')
                        dataFile.write( cloud_token)
                        dataFile.close()
                        dataFile = open('./refreshToken.txt', 'w')
                        dataFile.write( cloud_token)
                        dataFile.close()   
                        self.Rtoken = cloud_token
                    elif (os.path.exists('./refreshToken.txt')): #assume refreshToken is newer
                        dataFile = open('./refreshToken.txt', 'r')
                        self.Rtoken = dataFile.read()
                        cloud_token = self.Rtoken
                        dataFile.close() 
                    else: #InputToken must exist (this should never trigger)
                        dataFile = open('./refreshToken.txt', 'w') 
                        dataFile.write( cloud_token)
                        dataFile.close()                   
                        self.Rtoken = cloud_token
                else: #first time input - must overwrite referehToken as well 
                    dataFile = open('./inputToken.txt', 'w')
                    dataFile.write( cloud_token)
                    dataFile.close()
                    dataFile = open('./refreshToken.txt', 'w')
                    dataFile.write( cloud_token)
                    dataFile.close()                        
                    self.Rtoken = cloud_token                    
            else: # nothing has changed - use refreshToken 
                if (os.path.exists('./refreshToken.txt')):
                    dataFile = open('./refreshToken.txt', 'r')
                    self.Rtoken = dataFile.read()
                    cloud_token = self.Rtoken
                    dataFile.close()
            '''
        else:
            self.poly.Notices['ct'] = 'Missing Cloud Refresh Token'
            cloud_token = ''
    
        local_valid = True
        if self.local_email == '' or self.local_password == '' or self.local_ip == '':
            logging.debug('local access true, cfg = {} {} {}'.format(self.local_email, self.local_password, self.local_ip))
            local_valid = True
            if self.local_email == '':
                self.poly.Notices['lu'] = 'Please enter the local user name'
                local_valid = False
            if self.local_password == '':
                self.poly.Notices['lp'] = 'Please enter the local user password'
                local_valid = False
            if self.local_ip == '':
                self.poly.Notices['ip'] = 'Please enter the local IP address'
                local_valid = False

        cloud_valid = True
        if  cloud_token == '':
            logging.debug('cloud access true, cfg = {} '.format( cloud_token))
            if cloud_token == '':
                self.poly.Notices['ct'] = 'Please enter the Tesla Refresh Token - see readme for futher info '
                cloud_valid = False

        if local_valid:
            logging.debug('Local access is valid, configure....')
            self.localAccess = True

        if cloud_valid:
            logging.debug('Cloud access is valid, configure....')
            self.cloudAccess = True
        #logging.debug ('Trying t initialize APIs local: {} and cloud: {}'.format(local_valid, cloud_valid))

        logging.debug('done with parameter processing')
        
    def stop(self):
        #self.removeNoticesAll()
        if self.TPW:
            self.TPW.disconnectTPW()
        self.setDriver('ST', 0 )
        logging.debug('stop - Cleaning up')


    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0
        
    def systemPoll(self, pollList):
        logging.debug('systemPoll')
        if self.TPW and self.nodeDefineDone and  self.TPW.systemReady:        
            if 'longPoll' in pollList:
                self.longPoll()
            elif 'shortPoll' in pollList:
                self.shortPoll()
        else:
            logging.info('Waiting for system/nodes to initialize')

    def shortPoll(self):
        logging.info('Tesla Power Wall Controller shortPoll')
        self.heartbeat()    
        if self.TPW.pollSystemData('critical'):
            for node in self.poly.nodes():
                node.updateISYdrivers('critical')
        else:
            logging.info('Problem polling data from Tesla system') 

        

    def longPoll(self):

        logging.info('Tesla Power Wall  Controller longPoll')

        if self.TPW.pollSystemData('all'):
            for node in self.poly.nodes():
                node.updateISYdrivers('all')
            self.Rtoken  = self.TPW.getRtoken()
            if self.Rtoken  != self.Parameters['REFRESH_TOKEN']:
                self.Parameters['REFRESH_TOKEN'] = self.Rtoken
        else:
            logging.error ('Problem polling data from Tesla system')

    def updateISYdrivers(self, level):
        logging.debug('System updateISYdrivers - ' + str(level))       
        if level == 'all':
            value = self.TPW.isNodeServerUp()
            if value == 0:
               self.longPollCountMissed = self.longPollCountMissed + 1
            else:
               self.longPollCountMissed = 0
            self.setDriver('GV2', value)
            self.setDriver('GV3', self.longPollCountMissed)     
            logging.debug('CTRL Update ISY drivers : GV2  value:' + str(value) )
            logging.debug('CTRL Update ISY drivers : GV3  value:' + str(self.longPollCountMissed) )
        elif level == 'critical':
            value = self.TPW.isNodeServerUp()
            self.setDriver('GV2', value)   
            logging.debug('CTRL Update ISY drivers : GV2  value:' + str(value) )
        else:
            logging.error('Wrong parameter passed: ' + str(level))
 


    def ISYupdate (self, command):
        logging.debug('ISY-update called')
        if self.TPW.pollSystemData('all'):
            self.updateISYdrivers('all')
            #self.reportDrivers()
            for node in self.nodes:
                #logging.debug('Node : ' + node)
                if node != self.address :
                    self.nodes[node].longPoll()
 
    id = 'controller'
    commands = { 'UPDATE': ISYupdate }
    drivers = [
            {'driver': 'ST', 'value':0, 'uom':2},
            {'driver': 'GV2', 'value':0, 'uom':25},
            {'driver': 'GV3', 'value':0, 'uom':71}
            ]

if __name__ == "__main__":
    try:
        #logging.info('Starting Tesla Power Wall Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start()
        polyglot.updateProfile()
        polyglot.setCustomParamsDoc()
        TeslaPWController(polyglot, 'controller', 'controller', 'TeslaPowerWall')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
