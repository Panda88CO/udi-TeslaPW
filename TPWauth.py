import time
import json
import hashlib
from datetime import datetime
import requests
import os
from requests_oauth2 import OAuth2BearerToken




PG_CLOUD_ONLY = False
PC = True
if PC:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOGGER = logging.getLogger('testLOG')
else:
    import udi_interface
    LOGGER = udi_interface.LOGGER

#import udi_interface
#LOGGER = udi_interface.LOGGER

#import LOGGER
MAX_COUNT = 6
class TPWauth:
    def __init__(self, email, password):
        self.CLIENT_ID = "81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384"
        self.CLIENT_SECRET = "c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3"
        self.TESLA_URL = "https://owner-api.teslamotors.com"

        self.email = email
        self.password = password
        self.state_str = 'ThisIsATest' 
        self.cookies = None
        self.data = {}
        
        try:
            if (os.path.exists('./refreshToken.txt')):
                dataFile = open('./refreshToken.txt', 'r')
                self.Rtoken = dataFile.read()
                dataFile.close()
        except Exception as e:
            LOGGER.error('Exception storeDaysData: '+  str(e))         
            LOGGER.error ('Failed to write ./refreshToken.txt')
            self.Rtoken = ''

        self.running = False

    def tesla_refresh_token(self):
        S = {}
        if self.Rtoken:
            data = {}
            data['grant_type'] = 'refresh_token'
            data['client_id'] = 'ownerapi'
            data['refresh_token']=self.Rtoken
            data['scope']='openid email offline_access'      
            resp = requests.post('https://auth.tesla.com/oauth2/v3/token', data=data)
            S = json.loads(resp.text)
            if 'refresh_token' in S:
                self.Rtoken = S['refresh_token']
            else:
                self.Rtoken = None
            data = {}
            data['grant_type'] = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
            data['client_id']=self.CLIENT_ID
            data['client_secret']=self.CLIENT_SECRET
            with requests.Session() as s:
                try:
                    s.auth = OAuth2BearerToken(S['access_token'])
                    r = s.post(self.TESLA_URL + '/oauth/token',data)
                    S = json.loads(r.text)
                    dataFile = open('./refreshToken.txt', 'w')
                    dataFile.write( self.Rtoken)
                    dataFile.close()

                except  Exception as e:
                    LOGGER.error('Exception __tesla_refersh_token: ' + str(e))
                    LOGGER.error('New Refresh Token must be generated')
                    self.Rtoken = None
                    pass
            
            time.sleep(1)
        return S


    