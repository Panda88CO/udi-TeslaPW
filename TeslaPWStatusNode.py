#!/usr/bin/env python3

import time

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)
               
class teslaPWStatusNode(udi_interface.Node):

    def __init__(self, polyglot, primary, address, name, TPW):
        super(teslaPWStatusNode, self).__init__(polyglot, primary, address, name)
        logging.info('_init_ Tesla Power Wall Status Node')
        self.ISYforced = False
        self.TPW = TPW
        self.address = address 
        self.name = name
        self.hb = 0

        polyglot.subscribe(polyglot.START, self.start, address)
        
    def start(self):                
        logging.debug('Start Tesla Power Wall Status Node')  
        while not self.TPW.systemReady:
            time.sleep(1)
        self.updateISYdrivers('all')

    def stop(self):
        logging.debug('stop - Cleaning up')
    
    def season2ISY(self, season):
        if season.upper() == 'WINTER':
            return(0)
        elif season.upper() == 'SUMMER':
            return(1)
        elif season != None:
            return(2)
        else:
            return (99)
        

    def period2ISY(self, period):
        if period.upper() == 'OFF_PEAK':
            return(0)
        elif period.upper() == 'PERTIAL_PEAK':
            return(1)
        elif period.upper() == 'PEAK':
            return(2)
        else:
            return (99) 

    def updateISYdrivers(self, level):
        if self.TPW.systemReady:

            logging.debug('StatusNode updateISYdrivers')
            tmp = self.TPW.getTPW_backup_time_remaining()
            logging.debug('GV0: {}'.format(tmp))
            self.setDriver('GV0', round(tmp,2))
            logging.debug('GV1: '+ str(self.TPW.getTPW_chargeLevel()))
            self.setDriver('GV1', self.TPW.getTPW_chargeLevel())
            logging.debug('GV2: '+ str(self.TPW.getTPW_operationMode()))
            self.setDriver('GV2', self.TPW.getTPW_operationMode())
            logging.debug('GV3: '+ str(self.TPW.getTPW_gridStatus()))
            self.setDriver('GV3', self.TPW.getTPW_gridStatus())
            logging.debug('GV4: '+ str(self.TPW.getTPW_onLine()))
            self.setDriver('GV4', self.TPW.getTPW_onLine())
            logging.debug('GV5: '+ str(self.TPW.getTPW_gridServiceActive()))
            self.setDriver('GV5', self.TPW.getTPW_gridServiceActive())
            logging.debug('GV6: '+ str(self.TPW.getTPW_chargeLevel()))
            self.setDriver('GV6', self.TPW.getTPW_gridSupply())
            logging.debug('GV9: '+ str(self.TPW.getTPW_chargeLevel()))
            self.setDriver('GV9', self.TPW.getTPW_gridSupply())
            logging.debug('GV12: '+ str(self.TPW.getTPW_load()))
            self.setDriver('GV12', self.TPW.getTPW_load())
            
            if level == 'all':
                self.setDriver('GV7', self.TPW.getTPW_daysBattery())
                self.setDriver('GV8', self.TPW.getTPW_yesterdayBattery())
                self.setDriver('GV10', self.TPW.getTPW_daysGrid())
                self.setDriver('GV11', self.TPW.getTPW_yesterdayGrid())
                self.setDriver('GV13', self.TPW.getTPW_daysConsumption())
                self.setDriver('GV14', self.TPW.getTPW_yesterdayConsumption())
                self.setDriver('GV15', self.TPW.getTPW_daysGeneration())
                self.setDriver('GV16', self.TPW.getTPW_yesterdayGeneration())
                self.setDriver('GV17', self.TPW.getTPW_daysGridServicesUse())
                self.setDriver('GV18', self.TPW.getTPW_yesterdayGridServicesUse())
                self.setDriver('GV17', self.TPW.getTPW_daysSolar())
                self.setDriver('GV20', self.TPW.getTPW_yesterdaySolar())    
                season, period, rate = self.TPW.getTPW_tariff_rate_state()
                logging.debug('GV21 ={} ,GV23= {},GV24={}'.format(rate, period, season) )    
                self.setDriver('GV21',round(rate,2))
                self.setDriver('GV23',self.period2ISY(period))
                self.setDriver('GV24',self.season2ISY(period))
        else:
            logging.debug('System not ready yet')


    def ISYupdate (self, command):
        logging.debug('ISY-update called')
        if self.TPW.pollSystemData('all'):
            self.updateISYdrivers('all')

 

    id = 'pwstatus'
    commands = { 'UPDATE': ISYupdate, 
                }


    drivers = [
            {'driver': 'GV0', 'value': 0, 'uom': 20},  #battery level
            {'driver': 'GV1', 'value': 0, 'uom': 51},  #battery level
            {'driver': 'GV2', 'value': 0, 'uom': 25},  #mode
            {'driver': 'GV3', 'value': 0, 'uom': 25},  #grid status
            {'driver': 'GV4', 'value': 0, 'uom': 25},  #on/off line
            {'driver': 'GV5', 'value': 0, 'uom': 25},  #grid services
            {'driver': 'GV6', 'value': 0, 'uom': 33},  #battery supply
            {'driver': 'GV7', 'value': 0, 'uom': 33},  #battery today
            {'driver': 'GV8', 'value': 0, 'uom': 33},  #battery yesterday
            {'driver': 'GV9', 'value': 0, 'uom': 33},  #grid supply
            {'driver': 'GV10', 'value': 0, 'uom': 33}, #grid today
            {'driver': 'GV11', 'value': 0, 'uom': 33}, #grid yesterday
            {'driver': 'GV12', 'value': 0, 'uom': 33}, #load
            {'driver': 'GV13', 'value': 0, 'uom': 33}, #consumption today
            {'driver': 'GV14', 'value': 0, 'uom': 33}, #consumption yesterday
            {'driver': 'GV15', 'value': 0, 'uom': 33}, #generation today
            {'driver': 'GV16', 'value': 0, 'uom': 33}, #generation yesterday
            {'driver': 'GV17', 'value': 0, 'uom': 33}, #grid service today
            {'driver': 'GV18', 'value': 0, 'uom': 33}, #grid service yesterday
            {'driver': 'GV19', 'value': 0, 'uom': 33}, #Solar today
            {'driver': 'GV20', 'value': 0, 'uom': 33}, #Solar yesterday
            {'driver': 'GV20', 'value': 0, 'uom': 33}, #Solar yesterday
            {'driver': 'GV21', 'value': 0, 'uom': 103}, #Current buy rate
            #{'driver': 'GV22', 'value': 0, 'uom': 103}, #Current sell rate
            {'driver': 'GV23', 'value': 99, 'uom': 25}, #Peak/Partial/offpeak
            {'driver': 'GV24', 'value': 99, 'uom': 25}, #Summer/Winter
           
           
            ]


