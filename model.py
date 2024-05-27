
class Model:
    "Model class all objects are derived fom it"
    
    def use_alias(self):
        return False
    
    def get_alias(self, key):
        return None

    def __getitem__(self, key):
        if hasattr(self, key): return getattr(self, key)
        return None

    def __setitem__(self, key, value):
        "Set value of  attributes"
        if hasattr(self, key): setattr(self, key, value)
        if self.use_alias() and self.get_alias(key): 
            setattr(self, self.get_alias(key), value)

    def setter(self, record:dict):
        "Set values from record to Model child object, includes mapping it"
        if not record or type(record) is str: return None
        for k in record.keys():
            if self.use_alias(): 
                self[self.map(k)] = record[k]
            else:
                self[k] = record[k]

        return self

    def asdict(self, exclude=[]):
        "Returns a dict of all attributes"
        keys = vars(self)
        data = {}
        for k in keys:
            if k in exclude: continue
            if not str(k).startswith('_') and str(k)!='id':
                data[k] = getattr(self, k)
                if type(data[k]) is list:
                    if data[k] and issubclass(type(data[k][0]), Model):
                        temp = []
                        for i in data[k]:
                            temp.append(i.asdict())
                        data[k] = temp
                
        return data

    def haskey(self, key):
        "Check if attribute is present in object"
        if hasattr(self, key): return True
        if not self.use_alias(): return False
        return self.get_alias(key)

    def map(self, key):
        "Map column to attribute, according to standard names from Excel template"
        alias = self.get_alias(key)
        if alias : return alias
        return key
    
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
                s += f"{filler}'{x}': " + Model._printup(obj[x], level+1) + "\n"
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

class AliasedModel(Model):
    def use_alias(self):
        return True    

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
        self._atributos={}
        self._mapa=[]

    def load_attributes(self, lista=[]):
        for a in lista:
            self._atributos[a.atributo] = a
            self._mapa.append(a.atributo)

    def isMandatory(self, key):
        a:Atributo = self._atributos.get(key)
        if not a: return False
        return bool(a.relevancia)

    def isVariant(self, key):
        a:Atributo = self._atributos.get(key)
        if not a: return False
        return int(a.variacion)
    
    def isnotVariant(self, key):
        a:Atributo = self._atributos.get(key)
        if not a: return False
        return bool(a.variacion)

class Market(Model):
    def __init__(self):
        self.id:int = 0
        self.market:str = None
        self.url_sitio:str = None

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

class Producto(AliasedModel):
    constructed=False
    _alias={}
    
    def get_alias(self, key):
        return Producto._alias.get(key,False)

    def construct():
        Producto.constructed=True
        Producto._alias={}
        Producto._alias['parent-sku'] = 'sku'
        Producto._alias['ruta-color_base']='base'
        Producto._alias['nombre_modelo']='n_modelo'
        Producto._alias['fecha-inicio']='date_created'
        Producto._alias['garantia']='warranty'
        Producto._alias['alto-paq']='palto'
        Producto._alias['ancho-paq']='pancho'
        Producto._alias['largo-paq']='plargo'
        Producto._alias['peso-paq']='ppeso'
        Producto._alias['tipo-publicacion']='listing_type_id'
        Producto._alias['pais']='origen'
        Producto._alias['Marca']='marca'
        Producto._alias['Modelo']='modelo'
        Producto._alias['n_modelo']='nombre_modelo'
    
    def __init__(self):
        self.id:int = 0
        self.product_id:int = 0
        self.sku:str = None
        self.nombre:str=None
        self.descripcion:str=''
        self.ficha:str=None
        self.alto:float= 0.00
        self.ancho:float = 0.00
        self.largo:float = 0.00
        self.peso:float = 0.000
        self.dias_embarque:int=0
        self.categoria_id:int=0
        self.filtro_id:int=0
        self.marca:str=None
        self.etiquetas:str=None
        self.modelo:str=None
        self.date_created=None
        self.atributos:list = []
        self.listing_type_id:str=None
        self.warranty:str=None
        self.nombre_modelo:str=None
        self.origen:int=0
        self.color:str=''
        self.base:str=''
        self.palto:float=None
        self.pancho:float=None
        self.plargo:float=None
        self.ppeso:float=None
        self.etiquetas_web:str=None
        self.taxcode:str=None
        if not Producto.constructed: Producto.construct()


class Variacion(AliasedModel):
    constructed=False
    _alias={}
    
    def get_alias(self, key):
        return Variacion._alias.get(key,False)

    def construct():
        Variacion.constructed=True
        Variacion._alias={}
        Variacion._alias['parent-sku'] = 'parent'
        Variacion._alias['SKU'] = 'sku'
        Variacion._alias['Código universal de producto']="gtin"
        Variacion._alias['color_base']='base'

    def __init__(self):
        self.product_id:int=0
        self.sku:str=None
        self.stock:int=0
        self.color:str=None
        self.base:str=None
        self.talla:str=None
        self.gtin:str=None
        self.video:str=None
        self.imagen1:str=None
        self.imagen2:str=None
        self.imagen3:str=None
        self.imagen4:str=None
        self.imagen5:str=None
        self.imagen6:str=None
        self.imagen7:str=None
        self.imagen8:str=None
        self.imagen9:str=None
        self.imagen10:str=None
        self.bullet1:str=None
        self.bullet2:str=None
        self.bullet3:str=None
        self.bullet4:str=None
        self.bullet5:str=None
        self.atributos:list = []
        self.parent:str=None
        if not Variacion.constructed: Variacion.construct()

class Componente(Model):
    def __init__(self):
        self.sku:str=None
        self.cantidad:int=0

class Kit(Model):
    def __init__(self):
        self.sku:str=None
        self.comentario:str=None
        self.componentes:list=[]
   

class Precio(AliasedModel):
    constructed=False
    _alias={}
    _markets={}
    
    def get_alias(self, key):
        return Precio._alias.get(key,False)

    def construct():
        Precio.constructed=True
        Precio._alias={}
        Precio._alias['sku'] = '_sku'
        Precio._alias['parent-sku'] = '_sku'
        Precio._alias['Marketplace'] = '_marketplace'
        Precio._alias['Precio'] = 'precio'
        Precio._alias['Oferta'] = 'oferta'        

    def __init__(self):
        self.market_id:int=0
        self.product_id:int = 0
        self.precio:float=0.00
        self.oferta:float=0.00
        self._sku:str=None
        self._marketplace:str=None
        if not Precio.constructed: Precio.construct()

    def get_market(self):
        if not self._marketplace: return 0
        return Precio._markets.get(self._marketplace.lower(), 0)

class Stock(AliasedModel):
    constructed=False
    _alias={}
    
    def get_alias(self, key):
        return Stock._alias.get(key,False)

    def construct():
        Stock.constructed=True
        Stock._alias={}
        Stock._alias['sku'] = 'seller_sku'
        Stock._alias['Hijo'] = 'seller_sku'
        Stock._alias['Stock'] = 'stock'

    def __init__(self):
        self.seller_sku:str = None
        self.product_id:int=0
        self.stock:int=0
        if not Stock.constructed: Stock.construct()


class Pedido(AliasedModel):
    constructed=False
    _alias={}
    
    def __init__(self):
        self.market_id=0
        self.referencia=''
        self.fecha_pedido=''
        self.fecha_autoriza=''
        self.subtotal=0.0
        self.total=0.0
        self.email=''
        self.entregara=''
        self.telefono=''
        self.direccion=''
        self.entrecalles=''
        self.colonia=''
        self.ciudad=''
        self.estado=''
        self.observaciones=''
        self.cp=''
        self.estatus=''
        self.mensajeria=''
        self.guias=''
        self.orden_id=None
        self.shipping_id=None
        self.fecha_orden=''
        self.lineas=[]

class Pedidodet(AliasedModel):
    constructed=False
    _alias={}
    def __init__(self):
        self.product_id=0
        self.sku=''
        self.descripcion=''
        self.fulfillment=''
        self.cantidad=0
        self.precio=0.0
        self.iva=0.0
        self.color=''
        self.referencia=''
        self.variacion=''
