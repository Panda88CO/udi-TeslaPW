#!/usr/bin/env python3

import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)
               
class teslaPWSolarNode(udi_interface.Node):

    def __init__(self, polyglot, primary, address, name, TPW):
        super(teslaPWSolarNode, self).__init__(polyglot, primary, address, name)
        logging.info('_init_ Tesla Power Wall Status Node')
        self.ISYforced = False
        self.TPW = TPW
        self.address = address 
        self.name = name
        self.hb = 0

        polyglot.subscribe(polyglot.START, self.start, address)
        
    def start(self):                
        logging.debug('Start Tesla Power Wall Solar Node')  
        while not self.TPW.systemReady:
            time.sleep(1)
        self.updateISYdrivers('all')

    def stop(self):
        logging.debug('stop - Cleaning up')
    
    def updateISYdrivers(self, level):
        if self.TPW.systemReady:
            logging.debug('SolarNode updateISYdrivers')
            self.setDriver('GV1', self.TPW.getTPW_solarSupply())

            if level == 'all':
                self.setDriver('GV2', self.TPW.getTPW_daysSolar())
                self.setDriver('GV3', self.TPW.getTPW_yesterdaySolar())
        else:
            logging.debug('System not ready yet')


    def ISYupdate (self, command):
        logging.debug('ISY-update called')
        if self.TPW.pollSystemData('all'):
            self.updateISYdrivers('all')
            #self.reportDrivers()
 

    id = 'pwsolar'
    commands = { 'UPDATE': ISYupdate, 
                }

    drivers = [
            {'driver': 'GV1', 'value': 0, 'uom': 33},  #Current solar supply
            {'driver': 'GV2', 'value': 0, 'uom': 33},  #solar power today
            {'driver': 'GV3', 'value': 0, 'uom': 33},  #solar power yesterday
            ]


