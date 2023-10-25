from model import Categoria,  Atributo, Producto, Model
from sdk import Controller, Categorias, Productos

class Parser():
    def __init__(self, controller:Controller, model:Model):
        self.controller:Controller = controller
        self.model = model

    def fetch_one(self, params=None, data={}):
        "Returns first record from api rest answer"
        data = self.controller.get(params, data)
        if data and data.get('answer'):
            for x in data.get('answer'):
                r:Model = self.model()
                return r.setter(x)

    def fetch_all(self, params=None, data={}, func=None, *args):
        "Returns all records from api rest answer"
        if func:
            rows = func(*args)
        else:
            rows = self.controller.get(params, data)
        todos = []
        if rows and rows.get('answer'):
            for x in rows.get('answer'):
                r:Model = self.model()
                todos.append(r.setter(x))
        return todos

    def fetch_raw(self, func, *args):
        "Returns raw answer from api rest"
        rows = func(*args)
        if rows and rows.get('answer'):  return rows.get('answer')
        return {}


        