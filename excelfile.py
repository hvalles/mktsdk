import os
from  enum import Enum
from openpyxl import load_workbook
from model import Producto, Categoria, Atributo, Kit, Variacion, Stock, Precio, Model

class ExcelType(Enum):
    ## Template clasification
    MASTER = 1
    KITS = 2
    PRICE = 4
    STOCK = 8
    VARIACION = 16

class Excelfile():
    COL_CATEGORIA=10
    def __init__(self, path, template:ExcelType):
        self.fname =path
        self.template = template
        self.first_row = 2
        self.wb = None
        self.hoja = None
        self.last_row = 1
        self.last_col = 1
        self.first_row = 1
        self.header = 1
        self.category:Categoria=None
        self.skus=[]
        self.master=0
   
    def start_row(self):
        "According to template return what row start data to consume"
        if self.template == ExcelType.MASTER: return 3
        return 2

    def new_model(self):
        "Creates  a new object according to template"
        if self.template==ExcelType.CATALOGO: return Producto()
        if self.template==ExcelType.KITS: return Kit()
        if self.template==ExcelType.PRECIOS: return Precio()
        if self.template==ExcelType.STOCK: return Stock()
        if self.template==ExcelType.VARIACION : return Variacion()
        raise TypeError()

    def parse_model(self, row:int=0, primary=True):
        "Read Excel row and return model object"
        r:Model = None
        if row:
            if self.template==ExcelType.MASTER:
                r = Producto() if primary else Variacion()
            else:
                r = self.new_model()
            for i in range(1,self.last_col+1):                
                col = self.hoja.cell(self.header, i).value
                if not col: continue
                value = self.hoja.cell(row, i).value
                z=r.haskey(col)
                print(type(r),col, z)
                if z:
                    if not value: value=''
                    r[col] = value
                if i>self.master and self.category and value and r.haskey('atributos') \
                    and len(self.category._mapa)>=(i-(self.master+1)):
                    col = self.category._mapa[i - (self.master+1)]
                    if primary and self.category.isnotVariant(col):
                        r.atributos.append({"atributo":col, 
                            "valor":self.hoja.cell(row, i).value})
                    if not primary and self.category.isVariant(col):
                        r.atributos.append({"atributo":col, 
                            "valor":self.hoja.cell(row, i).value})

        return r

    def read_row(self):
        "Generator for each row into model"
        for i in range(self.first_row, self.last_row+1):
            if self.template==ExcelType.MASTER: # Yields 2 records
                sku = self.hoja[f"A{i}"].value
                if not sku in self.skus:
                    yield self.parse_model(i)
                    self.skus.append(sku)
                yield self.parse_model(i, False)
            else:
                yield self.parse_model(i)

    def open(self, sheet=None):
        "Open excel file and set initial values"
        if not os.path.exists(self.fname): raise FileExistsError()
        self.wb = load_workbook(filename=self.fname, data_only=True)
        self.hoja = self.wb.active
        if sheet: self.hoja = self.wb[sheet]
        self.last_row = self.hoja.max_row
        self.last_col = self.hoja.max_column
        self.first_row = self.start_row()
        self.header = self.first_row - 1
        return self

