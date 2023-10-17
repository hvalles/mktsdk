import os
import aiosqlite
import asyncio
from sdk import Auth, Controller, Productos
from dotenv import load_dotenv

load_dotenv()

dbfile = "data/file.db"
db = None
auth = None

async def drop():
    db = await aiosqlite.connect(dbfile)
    sql = "SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='items';"
    cursor = await db.execute(sql)
    row = await cursor.fetchone()    
    if not row or not row[0]: return False
    sql = "drop table items;"
    cursor = await db.execute(sql)
    await db.close()
    return True

async def create():    
    db = await aiosqlite.connect(dbfile)
    sql = "SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='items';"
    cursor = await db.execute(sql)
    row = await cursor.fetchone()
    if row and row[0]: return False
    sql = """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL,
            nombre TEXT NOT NULL
        );"""
    cursor = await db.execute(sql)
    sql = "CREATE UNIQUE INDEX item_sku ON items(sku);"
    cursor = await db.execute(sql)
    await db.close()
    return True

async def get_item(id=0) :
    if id:
        cursor = await db.execute('SELECT * FROM items where id=%s;',(id))
        row = await cursor.fetchone()
    else:
        cursor = await db.execute('SELECT * FROM items order by id;',())
        row = await cursor.fetchall()
        await cursor.close()
    return row

def getAnswer(data):
    if data.get('answer'):
        for x in data.get('answer'):
            yield x

def showAnswer(data):
    if data.get('answer'):
        for x in data.get('answer'):
            print(x)

async def recoverItems():
    db = await aiosqlite.connect(dbfile)
    productos = Productos('productos', auth=auth)
    total = await productos.get_conteo()
    pages = total // 250
    sql = "insert or ignore into items (id, sku, nombre) values (?, ?, ?);"
    for i in range(0,pages):
        items = await productos.get_listado(250, 250 * i)
        for x in getAnswer(items):
            print (x['id'], x['sku'], x['nombre'])
            await db.execute(sql, (x['id'], x['sku'], x['nombre']))
        await db.commit()    
        asyncio.sleep(1.0)
    await db.close()

async def main():
    global auth
    await create()
    token = os.getenv('TOKEN')
    private = os.getenv("PRIVATE")
    auth = Auth(token=token, private=private)
    # colores = Controller('colores', auth=auth)
    # showAnswer(await colores.get())
    await recoverItems()  
    await asyncio.sleep(.25)

asyncio.run(main())