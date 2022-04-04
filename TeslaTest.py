
import sys
import time
import json
import os
import requests
import sys
from datetime import datetime
#from requests_MgcedMoauth2 import OAuth2BearerToken
#from TeslaToken import Token
from TeslaPWApi  import TeslaPWApi
#from powerwall1 import Powerwall

from TeslaInfo import tesla_info
#from ISYprofile import isyHandling
from datetime import date
PG_CLOUD_ONLY = False
PC = True
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('testLOG')


#import udi_interface
#LOGGER = udi_interface.LOGGER


#from TeslaLocalAPI import TeslaLocalAPI

#testAPI = TeslaLocalAPI('christian.olgaard@gmail.com','coe123COE', '192.168.1.151' )
#test1 = testAPI.teslaLocalConnect('christian.olgaard@gmail.com','coe123COE')
#test2 = testAPI.teslaGetBatteryInfo() 
#testAPI = TeslaCloudAPI('christian.olgaard@gmail.com','coe123COE')

#testAPI.teslaCloudConnect('christian.olgaard@gmail.com' , 'coe123COE')

#testAPI.teslaGetProduct()
print('\n\n Start')

#ISYapiC = tesla_info('christian.olgaard@gmail.com', 'coe123COE', 'test123', 't123',)
#test = ISYapiC.TPWcloud.refresh_T()

#ISYapiC.pollSystemData('critical')

'''
ISYapiC.pollSystemData('all')
#ISYapiC.createISYsetup()
ISYparams = ISYapiC.supportedParamters('pwsetup')
ISYcriticalParams = ISYapiC.criticalParamters('pwsetup')
for key in ISYparams:
    info = ISYparams[key]
    if info != {}:
        value = ISYapiC.getISYvalue(key, 'pwsetup')
        print('Update ISY drivers :' + str(key)+ ' ' + info['systemVar']+ ' value:' + str(value) )
        #self.setDriver(key, value, report = True, force = False)          
driversC = []
for key in ISYparams:
    info = ISYparams[key]
    if info != {}:
        value = ISYapiC.getISYvalue(key,  'pwsetup')
        driversC.append({'driver':key, 'value':value, 'uom':info['uom'] })
'''

#captchaAPIkey =  '850fa21e5b5baafb2b27212069aa6e6b'
'''
ISYapi = tesla_info('test123', 't123',  True, True)
#ISYapi.loginLocal('christian.olgaard@gmail.com', 'coe123COE', '192.168.1.151')
ISYapi.teslaInitializeData()
ISYapi.pollSystemData('all')
print('local')

if (os.path.exists('./refreshToken.txt')):
            dataFile = open('./refreshToken.txt', 'r')
            rtoken = dataFile.read()
            dataFile.close()
else:
    #rtoken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlR3bjV2bmNQUHhYNmprc2w5SUYyNnF4VVFfdyJ9.eyJpc3MiOiJodHRwczovL2F1dGgudGVzbGEuY29tL29hdXRoMi92MyIsImF1ZCI6Imh0dHBzOi8vYXV0aC50ZXNsYS5jb20vb2F1dGgyL3YzL3Rva2VuIiwiaWF0IjoxNjQ5MTA2OTQzLCJzY3AiOlsib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiXSwiZGF0YSI6eyJ2IjoiMSIsImF1ZCI6Imh0dHBzOi8vb3duZXItYXBpLnRlc2xhbW90b3JzLmNvbS8iLCJzdWIiOiI2MTI2OGM3OS1hNWM2LTRkNzQtYmNkMS05NTA4OWQ2MmExNzIiLCJzY3AiOlsib3BlbmlkIiwiZW1haWwiLCJvZmZsaW5lX2FjY2VzcyJdLCJhenAiOiJvd25lcmFwaSIsImFtciI6WyJwd2QiXSwiYXV0aF90aW1lIjoxNjQ5MTA2OTQzfX0.jaGVc4EJJ-b0ru0kRKCphNVpfm60D62qL4ftHp79EfWvelvSq5enqUstP8gLsIBKKXf9eAIvssjf9lhcArujrLQYDU3ILRToJ5Ji0SXbjhAIK8sIj5_cePDnrxPqO1k8-mNLj3b5YNMowa6ntQMVuLp-F0SL7P2DC6wB5po81JmMS_D8gkF_xOC52G-UQm3mnst-ZWeVYp3ZE6xQHJk8eZRhOHEp-VxxNCCt7FHpGaZq_2-E8oFkgwQezCUZ6nbZu4dwAlZJMGsPKbzn4ybj3ewoPWoEpKPNnsk79jdcwkgzSoIWd0hgAHhXg66SUFK_-x7jnrYYseQdYb6tiwm8Sg'
    file = open('./refreshToken.txt', 'w')
    file.write(rtoken)
    file.close()
'''

rtoken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlR3bjV2bmNQUHhYNmprc2w5SUYyNnF4VVFfdyJ9.eyJpc3MiOiJodHRwczovL2F1dGgudGVzbGEuY29tL29hdXRoMi92MyIsImF1ZCI6Imh0dHBzOi8vYXV0aC50ZXNsYS5jb20vb2F1dGgyL3YzL3Rva2VuIiwiaWF0IjoxNjQ5MTA2OTQzLCJzY3AiOlsib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiXSwiZGF0YSI6eyJ2IjoiMSIsImF1ZCI6Imh0dHBzOi8vb3duZXItYXBpLnRlc2xhbW90b3JzLmNvbS8iLCJzdWIiOiI2MTI2OGM3OS1hNWM2LTRkNzQtYmNkMS05NTA4OWQ2MmExNzIiLCJzY3AiOlsib3BlbmlkIiwiZW1haWwiLCJvZmZsaW5lX2FjY2VzcyJdLCJhenAiOiJvd25lcmFwaSIsImFtciI6WyJwd2QiXSwiYXV0aF90aW1lIjoxNjQ5MTA2OTQzfX0.jaGVc4EJJ-b0ru0kRKCphNVpfm60D62qL4ftHp79EfWvelvSq5enqUstP8gLsIBKKXf9eAIvssjf9lhcArujrLQYDU3ILRToJ5Ji0SXbjhAIK8sIj5_cePDnrxPqO1k8-mNLj3b5YNMowa6ntQMVuLp-F0SL7P2DC6wB5po81JmMS_D8gkF_xOC52G-UQm3mnst-ZWeVYp3ZE6xQHJk8eZRhOHEp-VxxNCCt7FHpGaZq_2-E8oFkgwQezCUZ6nbZu4dwAlZJMGsPKbzn4ybj3ewoPWoEpKPNnsk79jdcwkgzSoIWd0hgAHhXg66SUFK_-x7jnrYYseQdYb6tiwm8Sg'

ISYapiC= tesla_info ('test123', 't123',  False, True)
#ISYapiC.loginCloud('christian.olgaard@gmail.com', 'coe123COE')
ISYapiC.teslaCloudConnect(rtoken)
ISYapiC.teslaInitializeData()
ISYapiC.pollSystemData('all')
print('cloud')

'''
time.sleep(60)
print('local')
ISYapi.pollSystemData('all')
#print('cloud')
ISYapi.pollSystemData('all')
#print()


#ISYapi.createISYsetup()
ISYparams = ISYapi.supportedParamters('t123')
ISYcriticalParams = ISYapi.criticalParamters('t123')

ISYparamsC = ISYapiC.supportedParamters('t123')
ISYcriticalParamsC = ISYapiC.criticalParamters('t123')

for key in ISYparams:
    info = ISYparams[key]
    if info != {}:
        value = ISYapi.getISYvalue(key, 't123')
        print('Update ISY drivers :' + str(key)+ ' ' + info['systemVar']+ ' value:' + str(value) )
        #self.setDriver(key, value, report = True, force = False)          
drivers = []
for key in ISYparamsC:
    info = ISYparams[key]
    if info != {}:
        value = ISYapi.getISYvalue(key,  't123')
        drivers.append({'driver':key, 'value':value, 'uom':info['uom'] })

nodeList = ISYapi.getNodeIdList()
for node in nodeList:
    name = ISYapi.getNodeName(node)

nodeListC = ISYapiC.getNodeIdList()
for node in nodeListC:
    name = ISYapiC.getNodeName(node)

res0 = ISYapi.TPWlocal.get_solars()
res1 = ISYapi.getTPW_chargeLevel()
res2 = ISYapi.getTPW_backoffLevel()
res2a = ISYapi.getTPW_onLine()
res2b = ISYapi.getTPW_ConnectedTesla()
res2d = ISYapi.getTPW_powerSupplyMode()
#res2e = ISYapi.get_operation_mode()
#res2f = ISYapi.
res3 = ISYapi.getTPW_gridStatus()
res4 = ISYapi.getTPW_solarSupply()
res5 = ISYapi.getTPW_batterySupply()
res6 = ISYapi.getTPW_gridSupply()
res7 = ISYapi.getTPW_load()
res8 = ISYapi.getTPW_daysSolar()
res9 = ISYapi.getTPW_daysConsumption()
res10 = ISYapi.getTPW_daysGeneration()
res11 = ISYapi.getTPW_daysBattery()
res12 = ISYapi.getTPW_daysGridServicesUse()
res13 = ISYapi.getTPW_daysGeneratorUse()
res14 = ISYapi.getTPW_operationMode()
res15 = ISYapi.getTPW_gridServiceActive()
res16 = ISYapi.getTPW_stormMode()
res17 = ISYapi.getTPW_touMode()
res18 = ISYapi.getTPW_touSchedule()
'''




res1c = ISYapiC.getTPW_chargeLevel()
res2c = ISYapiC.getTPW_backoffLevel()
res2b = ISYapiC.getTPW_onLine()
res3c = ISYapiC.getTPW_gridStatus()
res4c = ISYapiC.getTPW_solarSupply()
res5c = ISYapiC.getTPW_batterySupply()
res6c = ISYapiC.getTPW_gridSupply()
res7c = ISYapiC.getTPW_load()
res8c = ISYapiC.getTPW_daysSolar()
res9c = ISYapiC.getTPW_daysConsumption()
res10c = ISYapiC.getTPW_daysGeneration()
res11c = ISYapiC.getTPW_daysBattery()
res12c = ISYapiC.getTPW_daysGridServicesUse()
res13c = ISYapiC.getTPW_daysGeneratorUse()
res14c = ISYapiC.getTPW_operationMode()
res15c = ISYapiC.getTPW_gridServiceActive()
res16c = ISYapiC.getTPW_stormMode()
res17c = ISYapiC.getTPW_touMode()
res18c = ISYapiC.getTPW_touSchedule()


print(f'getTPW_chargeLevel : {str(res1)}  {str(res1c)}\n')
print(f'getTPW_backupLevel : {str(res2)}  {str(res2c)}\n')
print(f'getTPW_backupLevel : {str(res2a)}  {str(res2b)}\n')
print(f'getTPW_gridStatus : {str(res3)}  {str(res3c)}\n')
print(f'getTPW_solarSupply : {str(res4)}  {str(res4c)}\n')
print(f'getTPW_batterySupply : {str(res5)}  {str(res5c)}\n')
print(f'getTPW_gridSupply : {str(res6)}  {str(res6c)}\n')
print(f'getTPW_load : {str(res7)}  {str(res7c)}\n')
print(f'getTPW_dailySolar : {str(res8)}  {str(res8c)}\n')
print(f'getTPW_dailyConsumption : {str(res9)}  {str(res9c)}\n')
print(f'getTPW_dailyGeneration : {str(res10)}  {str(res10c)}\n')
print(f'getTPW_dailyBattery : {str(res11)}  {str(res11c)}\n')
print(f'getTPW_dailyGridServicesUse : {str(res12)}  {str(res12c)}\n')
print(f'getTPW_dailyGeneratorUse : {str(res13)}  {str(res13c)}\n')
print(f'setTPW_operationMode : {str(res14)}  {str(res14c)}\n')
print(f'getTPW_gridServiceActive : {str(res15)}  {str(res15c)}\n')
print(f'getTPW_stormMode : {str(res16)}  {str(res16c)}\n')
print(f'getTPW_touMode : {str(res17)}  {str(res17c)}\n')
print(f'getTPW_touSchedule : {str(res18)}  {str(res18c)}\n')

print('end')

'''
site_info = testAPI.teslaGetSiteInfo('site_info')
list7 = testAPI.teslaExtractTouScheduleList(site_info)
list1 = testAPI.teslaAddToTouScheduleList(None, 'peak', 'weekend',16*60*60, 21*60*60)
list2 = testAPI.teslaAddToTouScheduleList(list1, 'off_peak','weekend',  0, 15*60*60)
list3 = testAPI.teslaAddToTouScheduleList(list2, 'peak','week',  16*60*60, 21*60*60)
list4 = testAPI.teslaAddToTouScheduleList(list3, 'off_peak','week',  22*60*60, 15*60*60)
res = testAPI.teslaSetTimeOfUseMode("balanced", list7)

stdout_fileno = sys.stdout
sys.stdout = open('.\cloud.txt', 'w')


product = testAPI.teslaGetProduct()
print('Product info')
print(product)


site_status = testAPI.teslaGetSiteInfo('site_status') # charge level
print('\n site_tatus ')
print(site_status)
site_live = testAPI.teslaGetSiteInfo('site_live')
print('\n site _live \n')
print(site_live)

site_info = testAPI.teslaGetSiteInfo('site_info') # defaule real mode, backup %
print('\n site _info \n')
print(site_info)
'''
#history = ISYapi.TPWcloud.site_history
#print('\n site _history \n')
##print(history)
#sys.stdout.close()
#sys.sdout = stdout_fileno


#dateStr = '2021-05-20T00:00:00-07:00'

#now = pytz.utc.localize(datetime.utcnow())

#now = pytz.utc.localize(datetime.utcnow())
'''
data = history['time_series']
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
    #LOGGER.debug(str(index) + ' ' + str(nbrRecords)+ ' '+ str(lastDuration))
loadPwr = gridPwr + solarPwr + batteryPwr + gridServicesPwr + generatorPwr

YsolarPwr = data[index]['solar_power']*timeFactor
YbatteryPwr = data[index]['battery_power']*timeFactor
YgridPwr = data[index]['grid_power']*timeFactor
YgridServicesPwr = data[index]['grid_services_power']*timeFactor
YgeneratorPwr = data[index]['generator_power']*timeFactor

prevObj = Obj
while ((prevObj.day == Obj.day) and  (prevObj.month == Obj.month) and (prevObj.year == Obj.year) and (index >= 1)):
    lastDuration =  prevObj - Obj
    timeFactor= lastDuration.total_seconds()/60/60
    YsolarPwr = YsolarPwr + data[index]['solar_power']*timeFactor
    YbatteryPwr = YbatteryPwr + data[index]['battery_power']*timeFactor
    YgridPwr = YgridPwr + data[index]['grid_power']*timeFactor
    YgridServicesPwr = YgridServicesPwr + data[index]['grid_services_power']*timeFactor
    YgeneratorPwr = YgeneratorPwr + data[index]['generator_power']*timeFactor

    index = index - 1
    prevObj = Obj
    dateStr = data[index]['timestamp']
    Obj = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")

YloadPwr = YgridPwr + YsolarPwr + YbatteryPwr + YgridServicesPwr + YgeneratorPwr




daysConsumption = {'solar_power': solarPwr, 'consumed_power': loadPwr, 'net_power':-gridPwr
                    ,'battery_power': batteryPwr ,'grid_services_power': gridServicesPwr, 'generator_power' : generatorPwr
                    ,'yesterday_solar_power': YsolarPwr, 'yesterday_consumed_power': YloadPwr, 'yesterday_net_power':-YgridPwr
                    ,'yesterday_battery_power': YbatteryPwr ,'yesterday_grid_services_power': YgridServicesPwr, 'yesterday_generator_power' : YgeneratorPwr, }



print(daysConsumption)

#grid = Net 
#powerConsumed = load

#test = testAPI.teslaGetStormMode()

print()
#bat_info = testAPI.teslaGetBatteryInfo('bat_info')
#bat_status = testAPI.teslaGetBatteryInfo('bat_status')
#bat_history = testAPI.teslaGetBatteryInfo('bat_history')
#energy_hist = testAPI.teslaGetBatteryInfo('energy_history')

'''
#test6 = testAPI.teslaExtractTouMode(site_info)
#test7 = testAPI.teslaExtractTouScheduleList(site_info)
'''

ENERGY_MODES = ["self_consumption", "autonomous", "backup"]
#testAPI.teslaSetOperationMode("autonomous")
TOU_MODES = ["economics", "balanced"]
#testAPI.teslaSetTimeOfUseMode("economics")
#testAPI.teslaSetBackupPercent(26)
#testAPI.teslaSetStormMode(False)

print()

'''
'''
drivers = []
PowerWall = Powerwall("192.168.1.151")
temp = PowerWall.login( 'coe123COE', 'christian.olgaard@gmail.com')

stdout_fileno = sys.stdout
sys.stdout = open('.\local.txt', 'w')
print(PowerWall.is_authenticated())
#testAPI.teslaGetBatteryInfo()




#PowerWall.close()
drivers = []
controllerName = 'powerwall'
id = 'tpwid'
TPW = tesla_info(None, None, controllerName, id, "christian.olgaard@gmail.com",  "coe123COE", "192.168.1.151")
ISYparams = TPW.supportedParamters(id)
for key in ISYparams:
    test = ISYparams[key]
    if  test != {}:
        val = TPW.getISYvalue(key, id)
        print(test['systemVar'] + ' : '+ str(val))
        
        drivers.append({'driver':key, 'value':val, 'uom':test['uom'] })
print()
test = TPW.getTPW_touMode()
test = TPW.getTPW_stormMode()
test = TPW.getTPW_operationMode()
test = TPW.getTPW_backupLevel()

for i in range(100):
    for key in ISYparams:
        test = ISYparams[key]
        if  test != {}:
            val = TPW.getISYvalue(key, id)
            print(test['systemVar'] + ' : '+ str(val))
    time.sleep(60)
    TPW.pollSystemData()
    print('\nineration : ' + str(i))


        #LOGGER.debug# LOGGER.debug(  'driver:  ' +  temp['driver'])

#self.teslaInfo = tesla_info('192.168.1.151', 'coe123COE', 'christian.olgaard@gmail.com')


#print(PowerWall.is_authenticated())
#print(PowerWall.get_charge())
#print(PowerWall.get_status()) 
#print(PowerWall.get_grid_status()) # ***
#print(PowerWall.get_site_info())

#metersOld = PowerWall.get_meters()
#time.sleep(60)


for i in range(3):
    meters = PowerWall.get_meters()
    print(meters.solar.instant_power,meters.solar.energy_exported, meters.solar.energy_imported, meters.solar.last_communication_time )
    print(meters.site.instant_power, meters.site.energy_exported, meters.site.energy_imported)
    print(meters.load.instant_power, meters.load.energy_exported, meters.load.energy_imported)
    print(meters.battery.instant_power, meters.battery.energy_exported, meters.battery.energy_imported)
    print()
    time.sleep(1)
print()


#print(PowerWall.run())
#print(PowerWall.stop())
#print(PowerWall.run())

print('get charge ') #needed
test1 = PowerWall.get_charge() #needed
print (test1)
print('\nget sitemaster ' )
test2 = PowerWall.get_sitemaster() #Needed
print (test2)

print(test2.is_connected_to_tesla, test2.is_running, test2.status)
print('\n get Meters ' )
print( PowerWall.get_meters())

print('\n get grid status ' ) # Needed
test3 = PowerWall.get_grid_status() # Needed
print(test3)

print('\n get grid services active ')
test4 = PowerWall.is_grid_services_active() # Needed
print(test4)

print('\n get operation mode ')
test5 = PowerWall.get_operation_mode()
print(test5)


print('\n get site info ')
test6 = PowerWall.get_site_info()
print(test6)
#testCOE1 = PowerWall.test_post("operation", {"default_real_mode":"self_consumption"})
#print(testCOE1)
test5 = PowerWall.get_operation_mode()
print(test5)
#testCOE1 = PowerWall.test_post("operation", {"default_real_mode":"autonomous"})
#print(testCOE1)
test5 = PowerWall.get_operation_mode()
print(test5)

BACKUP = "backup"
SELF_CONSUMPTION = "self_consumption"
AUTONOMOUS = "autonomous"
SCHEDULER = "scheduler"
SITE_CONTROL = "site_control"

#"self_consumption", "autonomous", "backup"]
#print(PowerWall.set_site_name(, site_name: str))

print('\n get status ')
test7 = PowerWall.get_status() # NEeded
print(test7)
#print(PowerWall.get_grid_status()) # Needed


print('\nget device type ')
print( PowerWall.get_device_type())
print('\n get device serial number ')
print( PowerWall.get_serial_numbers())
print('\n get operation mode')
print(PowerWall.get_operation_mode()) #Needed

print('\n get backup percentage ')
print( PowerWall.get_backup_reserve_percentage()) #Needed
print('\n get solar system ')
print( PowerWall.get_solars())

print('\n get power weall Vin')
print( PowerWall.get_vin())

print('\n get power wall version ')
print( PowerWall.get_version())

print('\n get detect and pin version')
print( PowerWall.detect_and_pin_version())


#print(PowerWall.pin_version(, vers: Union[str, version.Version]))


print(PowerWall.get_pinned_version())


print(PowerWall.get_api())


print('close ')

PowerWall.close()
sys.stdout.close()
sys.sdout = stdout_fileno
#print(PowerWall.logout())
'''