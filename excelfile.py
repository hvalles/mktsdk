from  enum import Enum
from openpyxl import load_workbook, Workbook
from model import Producto, Categoria, Atributo, Kit, Variacion, Stock, Precio

class ExcelType(Enum):
    ## Template clasification
    MASTER = 1
    KITS = 2
    PRICE = 4
    STOCK = 8


class Excelfile():
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
        if template==Excelfile.CATALOGO: self.first_row=3
   
    def start_row(self):
        "According to template return what row start data to consume"
        if self.template == ExcelType.MASTER: return 3
        return 2

    def new_model(self, primary=True):
        "Creates  a new object according to template"
        if self.template==Excelfile.CATALOGO: 
            if primary: return Producto()
            return Variacion()
        if self.template==Excelfile.KITS: return Kit()
        if self.template==Excelfile.PRECIOS: return Precio()
        if self.template==Excelfile.STOCK: return Stock()        
        raise TypeError()

    def parse_model(self, row:int=0, primary=True):
        "Read Excel row and return model object"
        r = None
        if row:
            r = self.new_model(primary)
            for i in range(1,self.last_col+1):
                r[self.hoja.cell(self.header, i).value()] = self.hoja.cell(row, i).value()
        return r

    def read_row(self, primary=True):
        "Generator for each row into model"
        for i in range(self.start_row, self.last_row+1):
            yield self.parse_model(i, primary)

    def open(self, sheet=None):
        "Open excel file and set initial values"
        self.wb = load_workbook(filename=self.fname, data_only=True)
        self.hoja = self.wb.active
        if sheet: self.hoja = self.wb[sheet]
        self.last_row = self.hoja.max_row
        self.last_col = self.hoja.max_column
        self.first_row = self.start_row()
        self.header = self.first_row - 1
