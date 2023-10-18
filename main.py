import os, sys, sqlite3, time
from sdk import Auth, Controller, Productos, Variaciones, Categorias
from dotenv import load_dotenv
from database import create, dbfile, drop, seconds, max_rows
from model import Categoria, Atributo

load_dotenv()
db = None
auth = None


def getAnswer(data):
    "Retrieve each recovered row from REST API Call."
    if data.get('answer'):
        for x in data.get('answer'):
            yield x

def showAnswer(data):
    "Show answer from REST Api for debugging only."
    if data.get('answer'):
        for x in data.get('answer'):
            print(x)

def recoverItems():
    "Retrieve all items and save them all in database, for verify later ids"
    print("Recover Items...")
    db = sqlite3.connect(dbfile)
    productos = Productos(auth=auth)
    total = productos.get_count()
    pages = total // max_rows
    sql = "insert or ignore into items (id, sku, nombre) values (?, ?, ?);"
    for i in range(0,pages):
        items = productos.get_list(max_rows, max_rows * i)
        for x in getAnswer(items):
            print (x['id'], x['sku'], x['nombre'])
            db.execute(sql, (x['id'], x['sku'], x['nombre']))
        db.commit()    
        time.sleep(seconds)
    print("End of process...")
    db.close()
    return True

def recoverChildren():
    "Retrieve all children and save them all in database, for verify later ids"
    print("Recover children...")
    db = sqlite3.connect(dbfile)
    children = Variaciones(auth=auth)
    total = children.get_count()
    pages = total // max_rows
    sql = "insert or ignore into children (id, sku, color, talla) values (?, ?, ?, ?);"
    for i in range(0,pages):
        items = children.get_list(max_rows, max_rows * i)
        for x in getAnswer(items):
            print (x['id'], x['sku'], x['color'], x['talla'])
            db.execute(sql, (x['id'], x['sku'], x['color'], x['talla']))
        db.commit()    
        time.sleep(seconds)
    print("End of process...")
    db.close()
    return True

def getCategory(id=0, path=''):
    "Retrieve Category by id or name"
    c = Categorias(auth)
    params={}
    if id: params['ids']=id
    if path: params['name']=path.replace('/',':')
    data = c.get(params)    
    todos = []
    for x in getAnswer(data):
        r = Categoria()
        todos.append(r.setter(x))
    return todos

def getAttributes(id:int=0):
    id = int(id)
    c = Categorias(auth)
    data = c.get_attributes(id)
    todos = []
    for x in getAnswer(data):
        r = Atributo()
        todos.append(r.setter(x))
    return todos

def raw_call(controller):
    # Example Raw Call
    c = Controller(controller, auth=auth)
    showAnswer(c.get())

def main():
    global auth
    create()
    token = os.getenv('TOKEN')
    private = os.getenv("PRIVATE")
    auth = Auth(token=token, private=private)
    #recoverItems()
    #recoverChildren()  
    cats = getCategory(0, '/Ropa,_Bolsas_y_Calzado/Playeras')
    c:Categoria = None
    for c in cats:
        print(c)
    attrs = getAttributes(c.id)
    a:Atributo = None
    for a in attrs:
        print(a)



if __name__ == '__main__':
    main()
