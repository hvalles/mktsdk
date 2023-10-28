import urllib
import requests
from datetime import datetime, timedelta
import hashlib
from hmac import HMAC
import json

class Auth():
    SANDBOX="https://sandbox.marketsync.mx/api"
    PRODUCTION="https://web.marketsync.mx/api"

    def __init__(self, private:str, token:str, production:bool=False) -> None:
        self.private = private
        self.token=token
        self.production=production
        self.parameters = {}

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
        self.parameters=parameters
        self.parameters['token'] = self.token
        self.parameters['timestamp'] = str(datetime.now().isoformat())[:19]
        self.parameters['version'] = '1.0'
        data = dict(sorted(self.parameters.items()))
        concatenated = str(urllib.parse.urlencode(data))
        url =self.getServer() + controller + concatenated + '&signature=' + self.signature(concatenated)
        print(url)
        return url

class Controller():    
    TIMEOUT=60.0
    def __init__(self, endpoint:str, auth:Auth=None) -> None:
        self.endpoint=endpoint
        self.auth = auth

    def check_answer(self, r):
        if not r: raise Exception(r.text)
        e = r.json().get('answer',{})
        if type(e) is dict:
            e = e.get('error')
            if e: raise Exception(e)

    def call(self, url, method="get", data=None):
        if not self.auth: raise Exception("Authorization  required!")
        if data:
            if method=='get':
                r = requests.get(url, json=data, timeout=self.TIMEOUT)
                if not r: raise Exception(r.text)
                return r.json()
            if method=='post':
                r = requests.post(url, json=data, timeout=self.TIMEOUT)
                self.check_answer(r)
                return r.json()
            if method=='put':
                r = requests.put(url, json=data, timeout=self.TIMEOUT)
                self.check_answer(r)
                return r.json()
            raise Exception("Method not allowed.")

        else:
            if method=='get':
                r = requests.get(url, timeout=self.TIMEOUT)
                return r.json()
            if method=='post':
                r = requests.post(url, timeout=self.TIMEOUT)
                return r.json()
            if method=='put':
                r = requests.put(url, timeout=self.TIMEOUT)
                return r.json()
            if method=='delete':
                r = requests.delete(url, timeout=self.TIMEOUT)
                return r.json()
            raise Exception("Method not allowed.")


    def get(self, key:dict=None, data:dict={}):        
        if not key: key={}
        url = self.auth.getUrl(self.endpoint, key)
        return self.call(url, "get", data)

    def post(self, data:dict={}):
        url = self.auth.getUrl(self.endpoint)
        return self.call(url, "post", data)

    def put(self, key:dict=None, data:dict={}):
        if not key: key={}
        url = self.auth.getUrl(self.endpoint)
        return self.call(url, "put", data)

    def delete(self, key:dict=None):
        if not key: key={}
        url = self.auth.getUrl(self.endpoint)
        return self.call(url, "delete")

class Colores(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='colores'
        self.auth = auth

class Categorias(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='categorias'
        self.auth = auth
    
    def get_attributes(self, category_id:int):
        category_id = int(category_id)
        url = self.auth.getUrl(self.endpoint+f"/atributos/{category_id}")
        return self.call(url, "get")

    def get_columns(self):
        url = self.auth.getUrl(self.endpoint+f"/columnas")
        return self.call(url, "get")


class Markets(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='markets'
        self.auth = auth

class Kits(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='kits'
        self.auth = auth

class Stocks(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='stock'
        self.auth = auth

class Precios(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='precios'
        self.auth = auth


class Productos(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='productos'
        self.auth = auth
        self.variacion:Controller = Variaciones(auth)

    def get_count(self):
        "Get total count of records"
        url = self.auth.getUrl(self.endpoint+"/countkeys")
        data = self.call(url, "get")
        answer = data.get('answer',[])
        if not answer: return 0
        return int(answer[0].get('total',0))

    def get_list(self, limit=250, offset=0, order="desc"):
        "Get list of records from server"
        url = self.auth.getUrl(self.endpoint+f"/listkeys/{limit}/{offset}/{order}")
        return self.call(url, "get")
    
class Variaciones(Controller):
    def __init__(self, auth:Auth=None) -> None:
        self.endpoint='variacion'
        self.auth = auth

    def get_count(self):
        "Get total count of records"
        url = self.auth.getUrl(self.endpoint+"/countkeys")
        data = self.call(url, "get")
        answer = data.get('answer',[])
        if not answer: return 0
        return int(answer[0].get('total',0))

    def get_list(self, limit=250, offset=0, order="desc"):
        "Get list of records from server"
        url = self.auth.getUrl(self.endpoint+f"/listkeys/{limit}/{offset}/{order}")
        return self.call(url, "get")

