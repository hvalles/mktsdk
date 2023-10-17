import urllib
import aiohttp
from datetime import datetime, timedelta
import hashlib
from hmac import HMAC
import json

class Auth():
    SANDBOX="https://sandbox.marketsync.mx/api"
    PRODUCTION="https://web.marketsync.mx/api"
    parameters = {}

    def __init__(self, private:str, token:str, production:bool=False) -> None:
        self.private = private
        self.token=token
        self.production=production

    def getServer(self):
        if self.production:
            return Auth.PRODUCTION
        else:
            return Auth.SANDBOX

    def signature(self, concatenated):  
        sign = HMAC(self.private.encode('utf-8'), concatenated.encode('utf-8'), hashlib.sha256).hexdigest()
        return str(sign)

    def getUrl(self, controller='', parameters:dict={}):
        if controller.find('?') == -1: controller+='?'
        if not controller.startswith('/') : controller ='/'+controller
        if bool(parameters): 
            self.parameters=parameters
        self.parameters['token'] = self.token
        self.parameters['timestamp'] = str(datetime.now().isoformat())[:19]
        self.parameters['version'] = '1.0'
        data = dict(sorted(self.parameters.items()))
        concatenated = str(urllib.parse.urlencode(data))
        return self.getServer() + controller + concatenated + '&signature=' + self.signature(concatenated)

class Controller():    
    def __init__(self, endpoint:str, auth:Auth=None) -> None:
        self.endpoint=endpoint
        self.auth = auth

    async def call(self, url, method="get", data=None):
        if not self.auth: raise Exception("Authorization  required!")
        if data:
            async with aiohttp.ClientSession() as session:
                if method=='get':
                    async with session.get(url, json=data) as resp:
                        return await resp.json()
                if method=='post':
                    async with session.post(url, json=data) as resp:
                        return await resp.json()
                if method=='put':
                    async with session.put(url, json=data) as resp:
                        return await resp.json()
                raise Exception("Method not allowed.")

        else:
            async with aiohttp.ClientSession() as session:
                if method=='get':
                    async with session.get(url) as resp:
                        return await resp.json()
                if method=='post':
                    async with session.post(url) as resp:
                        return await resp.json()
                if method=='put':
                    async with session.put(url) as resp:
                        return await resp.json()
                if method=='delete':
                    async with session.delete(url) as resp:
                        return await resp.json()
                raise Exception("Method not allowed.")


    async def get(self, key:dict=None, data:dict={}):        
        if not key: key={}
        url = self.auth.getUrl(self.endpoint, key)
        return await self.call(url, "get", data)

    async def post(self, data:dict={}):
        url = self.auth.getUrl(self.endpoint)
        return await self.call(url, "post", data)

    async def put(self, key:dict, data:dict={}):
        if not key: key={}
        url = self.auth.getUrl(self.endpoint, key)
        return await self.call(url, "put", data)

    async def delete(self, key:dict):
        if not key: key={}
        url = self.auth.getUrl(self.endpoint, key)
        return await self.call(url, "put")


class Productos(Controller):

    async def get_conteo(self):
        url = self.auth.getUrl(self.endpoint+"/countkeys")
        data = await self.call(url, "get")
        answer = data.get('answer',[])
        if not answer: return 0
        return int(answer[0].get('total',0))

    async def get_listado(self, limit=250, offset=0, order="desc"):
        url = self.auth.getUrl(self.endpoint+f"/listkeys/{limit}/{offset}/{order}")
        return await self.call(url, "get")

