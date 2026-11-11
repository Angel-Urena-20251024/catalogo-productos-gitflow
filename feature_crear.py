"""Registro de productos con validación en el servidor."""
from app import connection, validate, public

def create(path, query, body):
    values = validate(body)
    with connection() as db:
        result = db.execute('INSERT INTO products(name,price_cents,stock) VALUES(?,?,?)', values)
        row = db.execute('SELECT * FROM products WHERE id=?', (result.lastrowid,)).fetchone()
    return 201, public(row)

def register(routes):
    routes['POST', '/api/products'] = create
