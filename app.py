import os,  sys, sqlite3, time, math
from tkinter.filedialog import askopenfilename
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar, messagebox, simpledialog
from sdk import Auth, Controller, Productos, Variaciones, Categorias, Kits, Stocks, Precios
from dotenv import load_dotenv
import database
from model import Categoria, Atributo, Producto, Stock, Variacion
from excelfile import ExcelType, Excelfile
from apiparser import Parser

load_dotenv()
class LoaderEngine(tb.Frame):
    MAX_ROWS = 50
    MAX_ERRORS = 10
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.filename=StringVar()
        self.archivo = StringVar()
        self.db = None
        self.auth=None
        self.master = master
        self.xls=None
        self.controller:Controller = None
        self.errors = 0

        token = os.getenv('TOKEN')
        private = os.getenv("PRIVATE")
        if token and private : self.auth = Auth(token=token, private=private)

        _path = os.path.dirname(os.path.realpath(__file__))
        _path = os.path.join(_path,"data")
        if not os.path.exists(_path): os.mkdir(_path)
        database.dbfile = os.path.join(_path,"file.db")

        # application variables
        row = 0
        tb.Button(text="Bajar Prods", bootstyle="info", command=self.recover).grid(
            row=row, column=1, padx=10, pady=5)

        tb.Button(text="Limpiar Datos", bootstyle="info", command=self.truncate).grid(
            row=row, column=3, padx=10, pady=5)

        tb.Button(text="Llaves", bootstyle="info", command=self.setkeys).grid(
            row=row, column=5, padx=10, pady=5)

        lista = ["Catalogo", "Precios", "Stock", "kits"]
        row+=2
        tb.Label(text="Tipo de archivo:").grid(row=row, column=1, padx=10, pady=5)
        self.cbo = tb.Combobox(master=master, values=lista, textvariable=self.archivo)
        self.cbo.grid(row=row, column=2, columnspan=2, padx=10,pady=5)
        self.cbo.current(0)

        self.action = StringVar()
        tb.Radiobutton(master, text='Insertar', variable=self.action, 
            value='insert').grid(row=row, column=4, padx=10, pady=5)
        tb.Radiobutton(master, text='Actualizar', variable=self.action, 
            value='update').grid(row=row, column=5, padx=10, pady=5)
        self.action.set("insert")

        row += 1
        tb.Label(text="Ruta (xlsx):").grid(row=row, column=1,  padx=10, pady=5)
        tb.Entry(master=master, width=50, textvariable=self.filename).grid(row=row, column=2, columnspan=3, padx=10,pady=5)
        tb.Button(text="Buscar", bootstyle="success", command=self.open_file).grid(row=row, 
            column=6, padx=10, pady=5)

        row +=2
        self.pb = tb.Progressbar(
            master=master,
            mode=DETERMINATE, 
            bootstyle=(STRIPED, SUCCESS),
            length=250
        )
        self.pb.grid(row=row, column=0, columnspan=6)

        row += 2
        tb.Button(text="Aceptar", bootstyle="primary", command=self.process).grid(
            row=row, column=2, padx=10, pady=5)
        tb.Button(text="Cancelar", bootstyle="danger", command=self.cancel).grid(
            row=row, column=4, padx=10, pady=5)

    def open_file(self):
        filename = askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        self.filename.set(filename)

    def process_chunk(self, data):
        primario = []
        secundario =[]
        catalogo = False
        for r in data:
            if type(r) is Producto: 
                catalogo = True
                r.categoria_id = self.xls.category.id
            if self.action.get()=='update':
                if type(r) is Producto:
                    sku = database.get_row(r.sku)
                    r['id'] = sku['id']
                elif type(r) in [Stock, Variacion]:
                    sku = database.get_row(r.sku,'children')
                    r['product_id'] = sku['product_id']                    
            if type(r) is Variacion:
                secundario.append(r.asdict())
            else:
                primario.append(r.asdict())
        try:
            if self.action.get()=='insert':
                if primario: 
                    primario = self.controller.post(primario)
                    if catalogo: database.add_item(primario.get('answer',[]))
                if secundario: 
                    if catalogo:
                        for x in secundario:
                            sku = database.get_row(x['parent'])
                            x['product_id'] = sku['id']       
                            del x['parent']             

                    secundario = self.controller.variacion.post(secundario)
            else:
                if primario: primario = self.controller.put(primario)
                if secundario: 
                    for x in secundario: del x['parent']             
                    secundario = self.controller.variacion.put(secundario)

            if secundario:
                database.add_children(secundario.get('answer',[]))
        except Exception as e:   
            print(str(e))     
            database.log_error(e)
            self.errors+=1
            if self.errors > self.MAX_ERRORS:
                messagebox.showerror("Error en aplicación", "Ha excedido el máximo de errores revise data/errors.log")
                sys.exit(0)

        return (primario, secundario)

    def process_file(self):
        def load_category():
            c:Categorias = Categorias(self.auth)
            cat = self.xls.hoja.cell(self.xls.first_row, self.xls.COL_CATEGORIA).value
            p = Parser(c, Categoria)
            self.xls.category = p.fetch_one({'name':cat})
            self.xls.master = p.fetch_raw(c.get_columns)
            self.xls.master = int(self.xls.master.get('columnas',0))
            p = Parser(c, Atributo)
            self.xls.category.load_attributes(p.fetch_all(None, {}, c.get_attributes, self.xls.category.id))

        def get_controller(idx):
            if idx==0: 
                tmp = ExcelType.MASTER
                controller = Productos(self.auth)
            elif idx==1: 
                tmp = ExcelType.PRICE
                controller=Precios(self.auth)
            elif idx==2: 
                tmp = ExcelType.STOCK
                controller=Stocks(self.auth)
            elif idx==3: 
                tmp = ExcelType.KITS
                controller=Kits(self.auth)
            else:
                raise TypeError("Opción no identificada")
            return tmp, controller

        tmp, self.controller = get_controller(self.cbo.current())
        self.xls = Excelfile(self.filename.get(),tmp)
        self.xls.open()
        self.errors=0
        if tmp == ExcelType.MASTER: load_category()
        self.pb['maximum'] = self.xls.last_row
        self.pb.start()
        i = 0
        j = 0
        data = []
        done = {}
        for r in self.xls.read_row() :
            data.append(r)
            i+=1;j+=1
            if j>=self.MAX_ROWS:
                j=0
                res = self.process_chunk(data)
                data=[]
            self.pb['value'] = i
            self.master.update()

        if j>0: self.process_chunk(data)
        self.pb.stop()

    def process(self):
        if not self.archivo.get(): 
            messagebox.showerror("Error en carga", "El tipo de carga es requerido")
            return
        if not self.filename.get(): 
            messagebox.showerror("Error en carga", "El archivo es requerido")
            return
        if not os.path.exists(self.filename.get()):
            messagebox.showerror("Error en carga", "El archivo no existe")
            return
        if not str(self.filename.get()).lower().endswith(".xlsx"):
            messagebox.showerror("Error en carga", "El La extensión del archivo no es la adecuada.")
            return
        if not str(self.action.get()).lower() in ['insert','update']:
            messagebox.showerror("Error en carga", "La acción se se ha definido.")
            return
        if not self.auth:
            messagebox.showerror("Error en carga", "Se requieren las credenciales para continuar.")
            return
        answer = messagebox.askyesno(title="Confirmación", message="Deseas proceder con la carga?")
        if not answer: return

        self.process_file()

    def cancel(self):
        "Cleansup all data frominterface"
        self.filename.set("")
        self.cbo.current(0)

    def truncate(self):
        "Removes all data from database"
        answer = messagebox.askyesno(title="Confirmación", message="Deseas eliminar la bdd?")
        if not answer: return
        database.drop()
        database.create()

    def setkeys(self):
        token = os.getenv('TOKEN')
        private = os.getenv("PRIVATE")
        token = simpledialog.askstring("Llaves de conexión", 
            "Introduzca token público:", initialvalue=token)
        private = simpledialog.askstring("Llaves de conexión", 
            "Introduzca llave privada:", initialvalue=private)
        if token and private : 
            self.auth = Auth(token=token, private=private)
            with open(".env","wt") as f:
                f.write(f"TOKEN={token}\n")
                f.write(f"PRIVATE={token}\n")

    def getAnswer(self, data):
        "Retrieve each recovered row from REST API Call."
        if data.get('answer'):
            for x in data.get('answer'):
                yield x

    def recover(self):
        "Retrieve all items and save them all in database, for verify later ids"
        db = sqlite3.connect(database.dbfile)
        productos = Productos(auth=self.auth)
        total = productos.get_count()        
        pages = math.ceil(total / database.max_rows)
        self.pb['maximum'] = pages
        self.pb['value'] = 0
        self.pb.start()
        sql = "insert or ignore into items (id, sku, nombre) values (?, ?, ?);"
        for i in range(0,pages):
            items = productos.get_list(database.max_rows, database.max_rows * i)
            for x in self.getAnswer(items):
                db.execute(sql, (x['id'], x['sku'], x['nombre']))
            db.commit()    
            self.pb['value'] = i
            self.master.update()
            time.sleep(database.seconds)
        self.pb['value'] = pages
        self.pb.stop()
        db.close()
        return self.recover_children()

    def recover_children(self):
        "Retrieve all children and save them all in database, for verify later ids"
        db = sqlite3.connect(database.dbfile)
        children = Variaciones(auth=self.auth)
        total = children.get_count()
        pages = math.ceil(total / database.max_rows)
        self.pb['maximum'] = pages
        self.pb['value'] = 0
        self.pb.start()
        sql = "insert or ignore into children (id, sku, product_id, color, talla) values (?, ?, ?, ?, ?);"
        for i in range(0,pages):
            items = children.get_list(database.max_rows, database.max_rows * i)
            for x in self.getAnswer(items):
                db.execute(sql, (x['id'], x['sku'], x['product_id'], x['color'], x['talla']))
            db.commit()    
            self.pb['value'] = i
            self.master.update()
            time.sleep(database.seconds)
        self.pb['value'] = pages
        self.pb.stop()

        db.close()
        return True


if __name__ == '__main__':

    theme = os.getenv("THEME", "cosmo")
    app = tb.Window("MarketSync Loader", theme)
    LoaderEngine(app)
    app.mainloop()