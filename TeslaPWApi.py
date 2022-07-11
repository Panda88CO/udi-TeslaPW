
from datetime import datetime
import requests

from requests_oauth2 import OAuth2BearerToken
from TeslaCloudApi import teslaCloudApi


PG_CLOUD_ONLY = False
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)


class TeslaPWApi():

    def __init__(self, Rtoken):

        self.loginData = {}
        self.tokenExpMargin = 600 #10min
        self.TESLA_URL = "https://owner-api.teslamotors.com"
        self.API = "/api/1"
        self.OPERATING_MODES = ["backup", "self_consumption", "autonomous"]
        self.TOU_MODES = ["economics", "balanced"]
        self.teslaApi = teslaCloudApi(Rtoken)

        self.daysConsumption = {}
        self.tokeninfo = {}
        self.touScheduleList = []
        self.connectionEstablished = False
        self.cloudAccess =  self.connectionEstablished
        self.products = {}
        self.site_id = ''
        self.Header= {'Accept':'application/json'}
        #self.battery_id = ''
        #self.teslaAuth = TPWauth(self.email, self.password)

    def teslaCloudConnect(self ):
        logging.debug('teslaCloudConnect')
        #self.tokeninfo = self.teslaAuth.tesla_refresh_token( )
        return(self.tokeninfo)

    def teslaRetrieveCloudData(self):
        if self.teslaCloudInfo(): 
            self.connectionEstablished = True
            self.site_status = self.teslaGetSiteInfo('site_status')
            self.cloudAccess = self.teslaUpdateCloudData('all')
            self.touSchedule = self.teslaExtractTouScheduleList()
        else:
            logging.error('Error getting cloud data')
            return(None)
        #logging.debug(self.site_info)    
        if 'tou_settings' in self.site_info:
            if 'optimization_strategy' in self.site_info['tou_settings']:
                self.touMode = self.site_info['tou_settings']['optimization_strategy']
            else:
                self.touMode = None
            if 'schedule' in self.site_info['tou_settings']:
                self.touScheduleList =self.site_info['tou_settings']['schedule']
            else:
                self.touScheduleList = []
        else:
            self.touMode = None
            self.touScheduleList = []
            logging.debug('Tou mode not set')

    '''
    Query the cloud for the different types of data.  If all
    data access fails (i.e. returns None), then return
    false to indicate that.

    Otherwise, return true to indiate that access is good
    '''
    def teslaUpdateCloudData(self, mode):
        if mode == 'critical':
            temp =self.teslaGetSiteInfo('site_live')
            if temp != None:
                self.site_live = temp
                return(True)
        elif mode == 'all':
            access = False
            temp= self.teslaGetSiteInfo('site_live')
            if temp != None:
                self.site_live = temp
                access = True
                
            temp = self.teslaGetSiteInfo('site_info')
            if temp != None:
                self.site_info = temp
                access = True
                
            
            temp = self.teslaGetSiteInfo('site_history_day')            
            if temp != None:
                self.site_history = temp
                access = True
            self.teslaCalculateDaysTotals()
            return(access)
        else:
            access = False
            temp= self.teslaGetSiteInfo('site_live')
            if temp != None:
                self.site_live = temp
                access = True
                
            temp = self.teslaGetSiteInfo('site_info')
            if temp != None:
                self.site_info = temp
                access = True
            
            temp = self.teslaGetSiteInfo('site_history_day')            
            if temp != None:
                self.site_history = temp
                access = True


            temp = self.teslaGetSiteInfo('site_status')
            if temp != None:
                self.site_status = temp
                access = True
            self.teslaCalculateDaysTotals()
            return(access)

    def supportedOperatingModes(self):
        return( self.OPERATING_MODES )

    def supportedTouModes(self):
        return(self.TOU_MODES)

    def teslaCloudInfo(self):
        if self.site_id == '':
            try:
                products = self.teslaGetProduct()
                nbrProducts = products['count']
                for index in range(0,nbrProducts): #Can only handle one power wall setup - will use last one found
                    if 'resource_type' in products['response'][index]:
                        if products['response'][index]['resource_type'] == 'battery':
                            self.site_id ='/'+ str(products['response'][index]['energy_site_id'] )
                            self.products = products['response'][index]
                return(True)
            except Exception as e:
                logging.error('Exception teslaCloudInfo: ' + str(e))
                return(False)
        else:
            return(True)

    '''
    def __teslaGetToken(self):
        if self.tokeninfo:
            dateNow = datetime.now()
            tokenExpires = datetime.fromtimestamp(self.tokeninfo['created_at'] + self.tokeninfo['expires_in']-self.tokenExpMargin)
            if dateNow > tokenExpires:
                logging.info('Renewing token')
                self.tokeninfo = self.teslaAuth.tesla_refresh_token()
        else:
            logging.error('New Refresh Token required - please generate  New Token')

        return(self.tokeninfo)


    def __teslaConnect(self):
        return(self.__teslaGetToken())

    '''
    def isConnectedToEV(self):
       return(self.teslaApi.isConnectedToTesla())

    def getRtoken(self):
        return(self.teslaApi.getRtoken())


    def teslaGetProduct(self):
        S = self.teslaApi.teslaConnect() 
        #S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])
                r = s.get(self.TESLA_URL + self.API + "/products", headers=self.Header)
                products = r.json()
                return(products)        
            except Exception as e:
                logging.error('Exception teslaGetProduct: '+ str(e))
                logging.error('Error getting product info')
                self.teslaApi.tesla_refresh_token( )
                return(None)



    def teslaSetOperationMode(self, mode):
        #if self.connectionEstablished:
        S = self.teslaApi.teslaConnect()
        #S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])          
                if mode  in self.OPERATING_MODES:
                    payload = {'default_real_mode': mode}
                    r = s.post(self.TESLA_URL +  self.API+ '/energy_sites'+self.site_id +'/operation', headers=self.Header, json=payload)        
                    site = r.json()
                    if site['response']['code'] <210:
                        self.site_info['default_real_mode'] = mode
                        return (True)
                    else:
                        return(False)
                else:
                    return(False)
                    #site="wrong mode supplied" + str(mode)
                #logging.debug(site)        
            except Exception as e:
                logging.error('Exception teslaSetOperationMode: ' + str(e))
                logging.error('Error setting operation mode')
                self.teslaApi.tesla_refresh_token( )
                return(False)

    def teslaExtractOperationMode(site_info):
        return(site_info['default_real_mode'])

    def teslaGetSiteInfo(self, mode):
        #if self.connectionEstablished:
        #S = self.__teslaConnect()
        S = self.teslaApi.teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])            
                if mode == 'site_status':
                    r = s.get(self.TESLA_URL + self.API+ '/energy_sites'+self.site_id +'/site_status', headers=self.Header)          
                    site = r.json()
                elif mode == 'site_live':
                    r = s.get(self.TESLA_URL + self.API+ '/energy_sites'+self.site_id +'/live_status', headers=self.Header)          
                    site = r.json()
                elif mode == 'site_info':
                    r = s.get(self.TESLA_URL + self.API+ '/energy_sites'+self.site_id +'/site_info', headers=self.Header)          
                    site = r.json()            
                elif mode == 'site_history_day':
                    r = s.get(self.TESLA_URL + self.API+ '/energy_sites'+self.site_id +'/history', headers=self.Header, json={'kind':'power', 'period':'day'}) 
                    site = r.json()                        
                else:
                    #logging.debug('Unknown mode: '+mode)
                    return(None)
                return(site['response'])
            except Exception as e:
                logging.error('Exception teslaGetSiteInfo: ' + str(e))
                logging.error('Error getting data' + str(mode))
                logging.error('Trying to reconnect')
                self.teslaApi.tesla_refresh_token( )
                return(None)

        
    def teslaGetSolar(self):
        return(self.products['components']['solar'])


    def teslaSetStormMode(self, EnableBool):
        #if self.connectionEstablished:
        S = self.teslaApi.teslaConnect()
        #S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])
                payload = {'enabled': EnableBool}
                r = s.post(self.TESLA_URL +  self.API+ '/energy_sites'+self.site_id +'/storm_mode', headers = self.Header, json=payload)
                site = r.json()
                if site['response']['code'] <210:
                    self.site_info['user_settings']['storm_mode_enabled'] = EnableBool
                    return (True)
                else:
                    return(False)
            except Exception as e:
                logging.error('Exception teslaSetStormMode: ' + str(e))
                logging.error('Error setting storm mode')
                self.teslaApi.tesla_refresh_token( )
                return(False)


    
    def teslaExtractStormMode(self):
        if self.site_info['user_settings']['storm_mode_enabled']:
            return(1)
        else:
            return(0)


    def teslaSetBackoffLevel(self, backupPercent):
        #if self.connectionEstablished:
        logging.debug('teslaSetBackoffLevel ' + str(backupPercent))
        S = self.teslaApi.teslaConnect()
        #S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])
                if backupPercent >=0 and backupPercent <=100:
                    payload = {'backup_reserve_percent': backupPercent}
                    r = s.post(self.TESLA_URL +  self.API + '/energy_sites'+self.site_id +'/backup', headers= self.Header,  json=payload)        
                    site = r.json()
                    if site['response']['code'] <210:
                        self.site_info['backup_reserve_percent'] = backupPercent
                        return (True)
                    else:
                        return(False)

                else:
                    return(False)
                    #site="Backup Percent out of range 0-100:" + str(backupPercent)
                    #logging.debug(site)   
            except  Exception as e:
                logging.error('Exception teslaSetBackoffLEvel: ' + str(e))
                logging.error('Error setting bacup percent')
                self.teslaApi.tesla_refresh_token( ) 
                return(False)


    def teslaExtractBackupPercent(self):
        return(self.site_info['backup_reserve_percent'])

    def teslaUpdateTouScheduleList(self, peakMode, weekdayWeekend, startEnd, time_s):
        indexFound = False
        try:
            if weekdayWeekend == 'weekend':
                days = set([6,0])
            else:
                days = set([1,2,3,4,5])

            if self.touScheduleList == None:
                self.touScheduleList = self.teslaExtractTouScheduleList()

            for index in range(0,len(self.touScheduleList)):
                if self.touScheduleList[index]['target']== peakMode and set(self.touScheduleList[index]['week_days']) == days:
                    indexFound = True
                    if startEnd == 'start':
                        self.touScheduleList[index]['start_seconds'] = time_s
                    else:
                        self.touScheduleList[index]['end_seconds'] = time_s
            if not(indexFound):
                temp = {}
                temp['target']= peakMode
                temp['week_days'] = days
                if startEnd == 'start':
                    temp['start_seconds'] = time_s
                else:
                    temp['end_seconds'] = time_s
                self.touScheduleList.append(temp)
                indexFound = True
            return(indexFound)
        except  Exception as e:
                logging.error('Exception teslaUpdateTouScheduleLite: ' + str(e))
                logging.error('Error updating schedule')
                #self.teslaApi.tesla_refresh_token( ) 
                return(False)

    def teslaSetTouSchedule(self, peakMode, weekdayWeekend, startEnd, time_s):
        if self.teslaUpdateTouScheduleList( peakMode, weekdayWeekend, startEnd, time_s):
            self.teslaSetTimeOfUse()

    def  teslaExtractTouTime(self, days, peakMode, startEnd ):
        indexFound = False
        try:
            if days == 'weekend':
                days =set([6,0])
            else:
                days = set([1,2,3,4,5])
            for index in range(0,len(self.touScheduleList)):
                if self.touScheduleList[index]['target']== peakMode and set(self.touScheduleList[index]['week_days']) == days:
                    if startEnd == 'start':
                        value = self.touScheduleList[index]['start_seconds']
                    else:
                        value = self.touScheduleList[index]['end_seconds']
                    indexFound = True
                    return(value)
            if not(indexFound):       
                self.site_info = self.teslaGetSiteInfo('site_info')
                self.touScheduleList = self.teslaExtractTouScheduleList()
                for index in range(0,len(self.touScheduleList)):
                    if self.touScheduleList[index]['target']== peakMode and set(self.touScheduleList[index]['week_days']) == days:
                        if startEnd == 'start':
                            value = self.touScheduleList[index]['start_seconds']
                        else:
                            value = self.touScheduleList[index]['end_seconds']
                        indexFound = True
                        return(value)
            if not(indexFound): 
                logging.debug('No schedule appears to be set')            
                return(-1)
        except  Exception as e:
            logging.error('Exception teslaExtractTouTime ' + str(e))
            logging.error('No schedule idenfied')
            return(-1)


    def teslaSetTimeOfUseMode (self, touMode):
        self.touMode = touMode
        self.teslaSetTimeOfUse()


    def teslaSetTimeOfUse (self):
        #if self.connectionEstablished:
        temp = {}
        S = self.teslaApi.teslaConnect() 
        #S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])
                temp['tou_settings'] = {}
                temp['tou_settings']['optimization_strategy'] = self.touMode
                temp['tou_settings']['schedule'] = self.touScheduleList
                payload = temp
                r = s.post(self.TESLA_URL +  self.API+ '/energy_sites'+self.site_id +'/time_of_use_settings', headers=self.Header, json=payload)
                site = r.json()
                if site['response']['code'] <210:
                    self.site_info['tou_settings']['optimization_strategy'] = self.touMode
                    self.site_info['tou_settings']['schedule']= self.touScheduleList
                    return (True)
                else:
                    return(False)
            except Exception as e:
                logging.error('Exception teslaSetTimeOfUse: ' + str(e))
                logging.error('Error setting time of use parameters')
                self.teslaApi.tesla_refresh_token( ) 
                return(False)

    def teslaExtractTouMode(self):
        return(self.site_info['tou_settings']['optimization_strategy'])

    def teslaExtractTouScheduleList(self):
        self.touScheduleList = self.site_info['tou_settings']['schedule']
        return( self.touScheduleList )

    def teslaExtractChargeLevel(self):
        return(round(self.site_live['percentage_charged'],2))
        
    def teslaExtractBackoffLevel(self):
        return(round(self.site_info['backup_reserve_percent'],1))

    def teslaExtractGridStatus(self): 
        return(self.site_live['island_status'])


    def teslaExtractSolarSupply(self):
        return(self.site_live['solar_power'])

    def teslaExtractBatterySupply(self):     
        return(self.site_live['battery_power'])

    def teslaExtractGridSupply(self):     
        return(self.site_live['grid_power'])

    def teslaExtractLoad(self): 
        return(self.site_live['load_power'])

    def teslaExtractGeneratorSupply (self):
        return(self.site_live['generator_power'])

    def teslaCalculateDaysTotals(self):
        try:
            data = self.site_history['time_series']
            nbrRecords = len(data)
            index = nbrRecords-1
            dateStr = data[index]['timestamp']
            Obj = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")

            solarPwr = 0
            batteryPwr = 0
            gridPwr = 0
            gridServicesPwr = 0
            generatorPwr = 0
            loadPwr = 0

            prevObj = Obj
            while ((prevObj.day == Obj.day) and  (prevObj.month == Obj.month) and (prevObj.year == Obj.year) and (index >= 1)):

                lastDuration =  prevObj - Obj
                timeFactor= lastDuration.total_seconds()/60/60
                solarPwr = solarPwr + data[index]['solar_power']*timeFactor
                batteryPwr = batteryPwr + data[index]['battery_power']*timeFactor
                gridPwr = gridPwr + data[index]['grid_power']*timeFactor
                gridServicesPwr = gridServicesPwr + data[index]['grid_services_power']*timeFactor
                generatorPwr = generatorPwr + data[index]['generator_power']*timeFactor

                index = index - 1
                prevObj = Obj
                dateStr = data[index]['timestamp']
                Obj = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")
            loadPwr = gridPwr + solarPwr + batteryPwr + generatorPwr # + gridServicesPwr

            ySolarPwr = data[index]['solar_power']*timeFactor
            yBatteryPwr = data[index]['battery_power']*timeFactor
            yGridPwr = data[index]['grid_power']*timeFactor
            yGridServicesPwr = data[index]['grid_services_power']*timeFactor
            YGeneratorPwr = data[index]['generator_power']*timeFactor

            prevObj = Obj
            while ((prevObj.day == Obj.day) and  (prevObj.month == Obj.month) and (prevObj.year == Obj.year) and (index >= 1)):
                lastDuration =  prevObj - Obj
                timeFactor= lastDuration.total_seconds()/60/60
                ySolarPwr = ySolarPwr + data[index]['solar_power']*timeFactor
                yBatteryPwr = yBatteryPwr + data[index]['battery_power']*timeFactor
                yGridPwr = yGridPwr + data[index]['grid_power']*timeFactor
                yGridServicesPwr = yGridServicesPwr + data[index]['grid_services_power']*timeFactor
                YGeneratorPwr = YGeneratorPwr + data[index]['generator_power']*timeFactor

                index = index - 1
                prevObj = Obj
                dateStr = data[index]['timestamp']
                Obj = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")

            yLoadPwr = yGridPwr + ySolarPwr + yBatteryPwr + YGeneratorPwr #gridservices


            self.daysConsumption = {'solar_power': solarPwr, 'consumed_power': loadPwr, 'net_power':gridPwr
                                ,'battery_power': batteryPwr ,'grid_services_power': gridServicesPwr, 'generator_power' : generatorPwr
                                ,'yesterday_solar_power': ySolarPwr, 'yesterday_consumed_power': yLoadPwr, 'yesterday_net_power':yGridPwr
                                ,'yesterday_battery_power': yBatteryPwr ,'yesterday_grid_services_power': yGridServicesPwr, 'yesterday_generator_power' : YGeneratorPwr, }
        
            #print(self.daysConsumption)
            return(True)
        except Exception as e:
            logging.error('Exception teslaCalculateDaysTotal: ' + str(e))
            logging.error(' Error obtaining time data')
  

    def teslaExtractDaysSolar(self):
        return(self.daysConsumption['solar_power'])
    
    def teslaExtractDaysConsumption(self):     
        return(self.daysConsumption['consumed_power'])

    def teslaExtractDaysGeneration(self):         
        return(self.daysConsumption['net_power'])

    def teslaExtractDaysBattery(self):         
        return(self.daysConsumption['battery_power'])

    def teslaExtractDaysGrid(self):         
        return(self.daysConsumption['net_power'])

    def teslaExtractDaysGridServicesUse(self):         
        return(self.daysConsumption['grid_services_power'])

    def teslaExtractDaysGeneratorUse(self):         
        return(self.daysConsumption['generator_power'])  

    def teslaExtractYesteraySolar(self):
        return(self.daysConsumption['yesterday_solar_power'])
    
    def teslaExtractYesterdayConsumption(self):     
        return(self.daysConsumption['yesterday_consumed_power'])

    def teslaExtractYesterdayGeneraton(self):         
        return(self.daysConsumption['yesterday_net_power'])

    def teslaExtractYesterdayBattery(self):         
        return(self.daysConsumption['yesterday_battery_power'])

    def teslaExtractYesterdayGrid(self):         
        return(self.daysConsumption['yesterday_net_power'])

    def teslaExtractYesterdayGridServiceUse(self):         
        return(self.daysConsumption['yesterday_grid_services_power'])

    def teslaExtractYesterdayGeneratorUse(self):         
        return(self.daysConsumption['yesterday_generator_power'])  

    def teslaExtractOperationMode(self):         
        return(self.site_info['default_real_mode'])
    '''
    def teslaExtractConnectedTesla(self):       
        return(True)

    def teslaExtractRunning(self):  
        return(True)
    '''
    #???
    def teslaExtractPowerSupplyMode(self):  
        return(True)

    def teslaExtractGridServiceActive(self):
        if self.site_live['grid_services_active']: 
            return(1)
        else:
            return(0)
