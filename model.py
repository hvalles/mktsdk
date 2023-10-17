
class Model:
    "Model class all objects are derived fom it"
    _columns = {}

    def __getattr__(self, name):
        "Obtains value of non register attributes"
        return self._columns.get(name)

    def __setattr__(self, name, value):
        "Set value of non register attributes"
        self._columns[name] = value

    def __delattr__(self, name):
        "Delete  non register attributes"
        del self._columns[name]

    @staticmethod
    def setter(self, record:dict):
        "Set values from record to Model child object"
        for k in record.keys():
            setattr(self, k, record[k])

        return self

    def asdict(self):
        "Returns a dict of all attributes"
        keys = vars(self)
        data = {}
        for k in keys:
            if not str(k).startswith('_') and str(k)!='id':
                data[k] = getattr(self, k)
        for k in self._columns.keys():
            if not str(k).startswith('_'):
                data[k] = self._columns.get(k)
                
        return data

    def clone(self):
        raise NotImplementedError

    @staticmethod
    def _printup(obj, level = 0):
        "Display structure of model"
        t = type(obj)
        s = ''
        filler = '  '*level
        if t in (str, type(None)):
            return f'{filler}{obj}'
        if t == int:
            return f"{filler}(int) {obj}"
        if t == bool:
            return f"{filler}(bool) {obj}"
        if t == float or str(t).find('Decimal') != -1:
            return f"{filler}(float) {obj}"

        if type(obj) in (list, set):
            if len(obj) == 0: return filler + "[]"
            s= filler + "[\n"
            for x in obj:
                s += Model._printup(x, level+1)+"\n"
            s+=filler+"]"
            return s
        
        if type(obj) is dict:
            if not bool(obj): return filler + "{}"            
            s=filler+"{\n"
            for x in obj.keys():
                s += f"{filler}'{x}': " + Model._printup(obj['x'], level+1) + "\n"
            s+=filler+"}"
            return s

        if hasattr(obj, '__dict__'):
            cols = vars(obj)
            s = filler+str(type(obj))+' {\n'
            for k in cols:
                v = getattr(obj, k)
                s += f"{filler}'{k}': " + Model._printup(v,level+1) + "\n"

            s += filler+'}'
            return s

        return str(obj)

    def __str__(self):
        return Model._printup(self)

class Color(Model):
    def __init__(self):
        self.id:int = 0
        self.color:str = None

class Categoria(Model):
    def __init__(self):
        self.id:int = 0
        self.categoria:str = None
        self.ruta:str = None
        self.permite_variacion:int = 0
        self.filtros:list = []

class Market(Model):
    def __init__(self):
        self.id:int = 0
        self.market:str = None
        self.url_sitio:str = None

class Valor(Model):
    def __init__(self):
        self.id:int = 0
        self.clave:str=None
        self.valor:str=None

class Atributo(Model):
    def __init__(self):
        self.id:int = 0
        self.orden:int = 0
        self.atributo:str=None
        self.nombre:str=None
        self.relevancia:int = 0
        self.tipo_valor:str=None
        self.tipo_long_max:int = 0
        self.variacion:int = 0
        self.valores:list = [] # valor
        self.unidades: list = [] # valor

class Producto(Model):
    def __init__(self):
        self.id:int = 0
        self.cliente_id:int = 0
        self.nombre:str=None
        self.descripcion:str=None
        self.ficha:str=None
        self.alto:float= 0.00
        self.ancho:float = 0.00
        self.largo:float = 0.00
        self.peso:float = 0.000
        self.sku:str = None
        self.dias_embarque:int=0
        self.categoria_id:int=0
        self.filtro_id:int=0
        self.marca:str=None
        self.etiquetas:str=None
        self.etiquetas_web:str=None
        self.modelo:str=None
        self.activo:int=0
        self.atributos:list = []
        self.origen:int=0
        self.warranty:str=None
        self.nombre_modelo:str=None
        self.palto:float=None
        self.pancho:float=None
        self.plargo:float=None
        self.ppeso:float=None
        self.taxcode:str=None
        self.color:str=None
        self.base:str=None

class Recurso(Model):
    def __init__(self):
        self.id:int=0
        self.valor:str=None

class Variacion(Model):
    def __init__(self):
        self.product_id:int=0
        self.sku:str=None
        self.stock:int=0
        self.color:str=None
        self.base:str=None
        self.talla:str=None
        self.gtin:str=None
        self.video:str=None
        self.imagenes:list=[] # Up to 10 Recursos
        self.bullets:list=[] # Up to 5 Recursos
        self.atributos:list = []
