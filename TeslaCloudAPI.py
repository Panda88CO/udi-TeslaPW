#!/usr/bin/env python3
import requests
import json
import time
from requests_oauth2 import OAuth2BearerToken


try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=30)



class teslaCloudApi(object):

    def __init__(self, refreshToken):
        logging.debug('teslaCloudApi')
        self.tokenInfo = None
        self.Rtoken = refreshToken
        self.tokenExpMargin = 600 #10min
        self.TESLA_URL = "https://owner-api.teslamotors.com"
        self.API = "/api/1"

        self.cookies = None
        self.data = {}
        
        self.tokenInfo = self.tesla_refresh_token()


    '''
    def isNodeServerUp(self):
        return( self.tokenInfo != None)
    '''

    def isConnectedToTesla(self):
        return( self.tokenInfo != None)     

    def teslaCloudConnect(self ):
        logging.debug('teslaCloudConnect')
        self.tokenInfo = self.tesla_refresh_token( )
        return(self.tokenInfo)


    def __teslaGetToken(self):
        if self.tokenInfo:
            dateNow = time.time()
            tokenExpires = self.tokenInfo['created_at'] + self.tokenInfo['expires_in']-self.tokenExpMargin
            if dateNow > tokenExpires:
                logging.info('Renewing token')
                self.tokenInfo = self.tesla_refresh_token()
        else:
            logging.error('New Refresh Token required - please generate  New Token')

        return(self.tokenInfo)


    def teslaConnect(self):
        return(self.__teslaGetToken())


    def teslaGetProduct(self):
        S = self.__teslaConnect()
        with requests.Session() as s:
            try:
                s.auth = OAuth2BearerToken(S['access_token'])
                r = s.get(self.TESLA_URL + self.API + "/products")
                products = r.json()
                return(products)        
            except Exception as e:
                logging.debug('Exception teslaGetProduct: '+ str(e))
                logging.error('Error getting product info')
                return(None)


    def getRtoken(self):
        return(self.Rtoken)

    def tesla_refresh_token(self):
        dateNow = int(time.time())
        S = {}
        if self.Rtoken:
            data = {}
            data['grant_type'] = 'refresh_token'
            data['client_id'] = 'ownerapi'
            data['refresh_token']=self.Rtoken
            data['scope']='openid email offline_access'      
            resp = requests.post('https://auth.tesla.com/oauth2/v3/token', data=data)
            S = json.loads(resp.text)
            S['created_at'] = dateNow
            if 'refresh_token' in S:
                self.Rtoken = S['refresh_token']
                #S['created_at'] = dateNow
                dataFile = open('./refreshToken.txt', 'w')
                dataFile.write( self.Rtoken)
                dataFile.close()


            '''
            data = {}
            data['grant_type'] = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
            data['client_id']=self.CLIENT_ID
            data['client_secret']=self.CLIENT_SECRET
            logging.info('tesla_refresh_token Rtoken : {}'.format(self.Rtoken ))

            with requests.Session() as s:
                try:
                    s.auth = OAuth2BearerToken(S['access_token'])
                    r = s.post(self.TESLA_URL + '/oauth/token',data)
                    S = json.loads(r.text)
                    
                    dataFile = open('./refreshToken.txt', 'w')
                    dataFile.write( self.Rtoken)
                    dataFile.close()
                    self.tokenInfo = S

                except  Exception as e:
                    logging.error('Exception __tesla_refersh_token: ' + str(e))
                    logging.error('New Refresh Token must be generated')
                    self.Rtoken = None
                    pass
            time.sleep(1)
            '''
        #logging.debug('tesla_refresh_token: {}'.format(S))
        return S

