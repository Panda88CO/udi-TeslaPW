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
    ISY = udi_interface.ISY
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
        self.TPW = None
        self.Parameters = Custom(polyglot, 'customParams')
        self.Notices = Custom(polyglot, 'notices')

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.check_config)

        self.n_queue = []
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))
        self.hb = 0
        self.poly.updateProfile()
        
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
        #self.poly.setCustomParamsDoc()
        # Wait for things to initialize....
        self.check_config()
        #while not self.initialized:
        #    time.sleep(1)
       
        if self.cloudAccess or self.localAccess:
            self.tesla_initialize(self.local_email, self.local_password, self.local_ip, self.Rtoken)
        else:
            self.poly.Notices['cfg'] = 'Tesla PowerWall NS needs configuration REFRESH_TOKEN and/or LOCAL_EMAIL, LOCAL_PASSWORD, LOCAL_IP_ADDRESS'
        
        while self.TPW == None:
            # Poll for current values (and update drivers)
            self.TPW.pollSystemData('all')
            self.updateISYdrivers('all')
        self.TPW.systemReady = True
   

    def check_config(self):
        logging.debug('check_config')
        if self.local_email == '':
            self.Parameters['LOCAL_USER_EMAIL'] = ''
        else:
            self.localAccess = True
        if self.local_password == '':
            self.Parameters['LOCAL_USER_PASSWORD'] = ''
        else:
            self.localAccess = True
        if self.local_ip == '':
            self.Parameters['LOCAL_IP_ADDRESS'] = ''
        else:
            self.localAccess = True

        if self.Rtoken == '':
            self.Parameters['REFRESH_TOKEN'] = ''
        else:
            self.cloudAccess = True
         

    '''
    This may be called multiple times with different settings as the user
    could be enabling or disabling the various types of access.  So if the
    user changes something, we want to re-initialize.
    '''
    def tesla_initialize(self, local_email, local_password, local_ip, Rtoken):
        logging.debug('starting Login process')
        try:

            self.TPW = tesla_info(self.name, self.address, self.localAccess, self.cloudAccess)
            if self.localAccess:
                logging.debug('Attempting to log in via local auth')
                try:
                    self.poly.Notices['localPW'] = 'Tesla PowerWall may need to be turned OFF and back ON to allow loacal access'
                    self.localAccessUp  = self.TPW.loginLocal(local_email, local_password, local_ip)
                    if self.localAccessUp:
                        self.poly.Notices.delete('localPW')
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
                temp = self.poly.getNode('solarstatus')
                if temp:
                    self.poly.delNode(temp)


            if self.TPW.generatorInstalled:
                if not self.poly.getNode('genstatus'):
                    node = teslaPWGenNode(self.poly, self.address, 'genstatus', 'Generator Status', self.TPW)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
            else:
                temp = self.poly.getNode('genstatus')
                if temp:
                    self.poly.delNode(temp)

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

    def handleParams (self, customParams ):
        logging.debug('handleParams')
        #supportParams = ['LOCAL_USER_EMAIL','LOCAL_USER_PASSWORD','LOCAL_IP_ADDRESS', 'REFRESH_TOKEN'   ]
        
        self.Parameters.load(customParams)

        #while customParams == None:
        #    logging.debug('handleParams load')
        #    time.sleep(1)
        #    #self.Parameters.load(customParams)
        
        self.poly.Notices.clear()
        cloud_valid = False
        local_valid = False
        self.localAccess = False
        self.cloudAccess = False
        #temp = self.Parameters
        '''
        for param in customParams:
            if param not in supportParams:
                del self.Parameters[param]
                logging.debug ('erasing key: ' + str(param))
        '''
        local_valid = True
        cloud_valid = True
        if self.Parameters.LOCAL_USER_EMAIL == None:
            self.poly.Notices['lu'] = 'Missing Local User Email parameter (LOCAL_USER_EMAIL)'
            self.local_email = ''
            local_valid = False
        else:
            self.local_email = self.Parameters.LOCAL_USER_EMAIL
            self.poly.Notices.delete('lu')    

        if self.Parameters.LOCAL_USER_PASSWORD == None:
            self.poly.Notices['lp'] =  'Missing Local User Password parameter (LOCAL_USER_PASSWORD)'
            self.local_password = ''
            local_valid = False
        else:
            self.local_password = self.Parameters.LOCAL_USER_PASSWORD
            self.poly.Notices.delete('lp')    

        if self.Parameters.LOCAL_IP_ADDRESS == None:
            self.poly.Notices['ip'] = 'Missing Local IP Address parameter (LOCAL_IP_ADDRESS)'
            self.local_ip = ''
            local_valid = False
        else:
            self.local_ip = self.Parameters.LOCAL_IP_ADDRESS 
            self.poly.Notices.delete('ip')    

        if self.Parameters.REFRESH_TOKEN == None:
            self.poly.Notices['ct'] = 'Missing Cloud Refresh Token (REFRESH_TOKEN)'
            self.Rtoken = ''
            cloud_valid = False 
        else:
            self.Rtoken = self.Parameters.REFRESH_TOKEN 
            self.poly.Notices.delete('ct')    
 
            
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
        self.poly.stop()
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
        logging.info('systemPoll {}'.format(pollList))
        if self.initialized:    
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
            if self.cloudAccess:
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
            if self.cloudAccess == False and self.localAccess == False:
                self.setDriver('GV4', 0)
            elif self.cloudAccess == True and self.localAccess == False:
                self.setDriver('GV4', 1)
            elif self.cloudAccess == False and self.localAccess == True:
                self.setDriver('GV4', 2)   
            elif self.cloudAccess == True and self.localAccess == True:
                self.setDriver('GV4', 3)   

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
            {'driver': 'ST', 'value':0, 'uom':25},
            {'driver': 'GV2', 'value':0, 'uom':25},
            {'driver': 'GV3', 'value':0, 'uom':55},
            {'driver': 'GV4', 'value':0, 'uom':25},
            ]

if __name__ == "__main__":
    try:
        #logging.info('Starting Tesla Power Wall Controller')
        polyglot = udi_interface.Interface([])
        polyglot.start('0.1.18')
        polyglot.updateProfile()
        polyglot.setCustomParamsDoc()
        TeslaPWController(polyglot, 'controller', 'controller', 'TeslaPowerWall')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
