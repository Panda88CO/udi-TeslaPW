#!/usr/bin/env python3

import time

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)

               
class teslaPWSetupNode(udi_interface.Node):

    def __init__(self, polyglot, primary, address, name, TPW):
        super(teslaPWSetupNode, self).__init__(polyglot, primary, address, name)

        logging.info('_init_ Tesla Power Wall setup Node')
        self.ISYforced = False
        self.TPW = TPW
        self.address = address 
        self.id = address
        self.name = name
        self.hb = 0

        self.poly.subscribe(self.poly.START, self.start, address)
        

    def start(self):                
        logging.debug('Start Tesla Power Wall Setup Node')  
        while not self.TPW.systemReady:
            time.sleep(1)
        self.updateISYdrivers('all')

    def stop(self):
        logging.debug('stop - Cleaning up')

    def updateISYdrivers(self, level):
        if self.TPW.systemReady:
            logging.debug('Node updateISYdrivers')
            self.setDriver('GV1', self.TPW.getTPW_backoffLevel())
            self.setDriver('GV2', self.TPW.getTPW_operationMode())
            self.setDriver('GV3', self.TPW.getTPW_stormMode())
            self.setDriver('GV4', self.TPW.getTPW_touMode())
            if level == 'all':
                val = self.TPW.getTPW_getTouData('weekend', 'off_peak', 'start')
                if val != -1:
                    self.setDriver('GV5', val, True, True, 58)
                else:
                    self.setDriver('GV5', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekend', 'off_peak', 'stop')
                if val != -1:
                    self.setDriver('GV6', val, True, True, 58)
                else:
                    self.setDriver('GV6', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekend', 'peak', 'start')
                if val != -1:
                    self.setDriver('GV7', val, True, True, 58)
                else:
                    self.setDriver('GV7', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekend', 'peak', 'stop')
                if val != -1:
                    self.setDriver('GV8', val, True, True, 58)
                else:
                    self.setDriver('GV8', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekday', 'off_peak', 'start')
                if val != -1:
                    self.setDriver('GV9', val, True, True, 58)
                else:
                    self.setDriver('GV9', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekday', 'off_peak', 'stop')
                if val != -1:
                    self.setDriver('GV10', val, True, True, 58)
                else:
                    self.setDriver('GV10', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekday', 'peak', 'start')
                if val != -1:
                    self.setDriver('GV11', val, True, True, 58)
                else:
                    self.setDriver('GV11', 99, True, True, 25)
                val = self.TPW.getTPW_getTouData('weekday', 'peak', 'stop')
                if val != -1:
                    self.setDriver('GV12', val, True, True, 58)
                else:
                    self.setDriver('GV12', 99, True, True, 25)

            logging.debug('updateISYdrivers - setupnode DONE')
        else:
            logging.debug('System Not ready yet')



    def setStormMode(self, command):
        logging.debug('setStormMode')
        value = int(command.get('value'))
        self.TPW.setTPW_stormMode(value)
        self.setDriver('GV3', value)
        
    def setOperatingMode(self, command):
        logging.debug('setOperatingMode')
        value = int(command.get('value'))
        self.TPW.setTPW_operationMode(value)
        self.setDriver('GV2', value)
    
    def setBackupPercent(self, command):
        logging.debug('setBackupPercent')
        value = float(command.get('value'))
        self.TPW.setTPW_backoffLevel(value)
        self.setDriver('GV1', value)

    def setTOUmode(self, command):
        logging.debug('setTOUmode')
        value = int(command.get('value'))
        self.TPW.setTPW_touMode(value)
        self.setDriver('GV4', value)

    def setWeekendOffpeakStart(self, command):
        logging.debug('setWeekendOffpeakStart')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('off_peak', 'weekend', 'start', value)
        self.setDriver('GV5', value)

    def setWeekendOffpeakEnd(self, command):
        logging.debug('setWeekendOffpeakEnd')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('off_peak', 'weekend', 'end', value)
        self.setDriver('GV6', value)

    def setWeekendPeakStart(self, command):
        logging.debug('setWeekendPeakStart')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('peak', 'weekend', 'start', value)
        self.setDriver('GV7', value)

    def setWeekendPeakEnd(self, command):
        logging.debug('setWeekendPeakEnd')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('peak', 'weekend', 'end', value)
        self.setDriver('GV8', value)

    def setWeekOffpeakStart(self, command):
        logging.debug('setWeekOffpeakStart')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('off_peak', 'week', 'start', value)
        self.setDriver('GV9', value)

    def setWeekOffpeakEnd(self, command):
        logging.debug('setWeekOffpeakEnd')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('off_peak', 'week', 'end', value)
        self.setDriver('GV10', value)

    def setWeekPeakStart(self, command):
        logging.debug('setWeekPeakStart')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('peak', 'week', 'start', value)
        self.setDriver('GV11', value)

    def setWeekPeakEnd(self, command):
        logging.debug('setWeekPeakEnd')
        value = int(command.get('value'))
        self.TPW.setTPW_updateTouSchedule('peak', 'week', 'end', value)
        self.setDriver('GV12', value)


    def ISYupdate (self, command):
        logging.debug('ISY-update called  Setup Node')
        if self.TPW.pollSystemData('all'):
            self.updateISYdrivers('all')
            #self.reportDrivers()
 

    id = 'pwsetup'
    commands = { 'UPDATE': ISYupdate
                ,'BACKUP_PCT' : setBackupPercent
                ,'STORM_MODE' :setStormMode
                ,'OP_MODE': setOperatingMode
                ,'TOU_MODE':setTOUmode
                ,'WE_O_PEAK_START': setWeekendOffpeakStart
                ,'WE_O_PEAK_END':setWeekendOffpeakEnd
                ,'WE_PEAK_START':setWeekendPeakStart
                ,'WE_PEAK_END':setWeekendPeakEnd
                ,'WK_O_PEAK_START':setWeekOffpeakStart
                ,'WK_O_PEAK_END':setWeekOffpeakEnd
                ,'WK_PEAK_START':setWeekPeakStart
                ,'WK_PEAK_END':setWeekPeakEnd

                }

    drivers = [
            {'driver': 'GV1', 'value': 0, 'uom': 51},  #backup reserve
            {'driver': 'GV2', 'value': 0, 'uom': 25},  #operating mode
            {'driver': 'GV3', 'value': 0, 'uom': 25},  #storm mode
            {'driver': 'GV4', 'value': 0, 'uom': 25},  #time of use mode
            {'driver': 'GV5', 'value': 0, 'uom': 58},  #weekend off start
            {'driver': 'GV6', 'value': 0, 'uom': 58},  #weekend off end
            {'driver': 'GV7', 'value': 0, 'uom': 58},  #weekend on start
            {'driver': 'GV8', 'value': 0, 'uom': 58},  #weekend on end
            {'driver': 'GV9', 'value': 0, 'uom': 58},  #weekday off start
            {'driver': 'GV10', 'value': 0, 'uom': 58}, #weekday off end
            {'driver': 'GV11', 'value': 0, 'uom': 58}, #weekday on start
            {'driver': 'GV12', 'value': 0, 'uom': 58}, #weekday on end
            ]

        

