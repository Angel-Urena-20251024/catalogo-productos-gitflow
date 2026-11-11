"""Consulta de productos y detalle individual."""
from app import connection, public, product_id

def listing(path, query, body):
    with connection() as db:
        rows = db.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    return 200, [public(row) for row in rows]

def detail(path, query, body):
    with connection() as db:
        row = db.execute('SELECT * FROM products WHERE id=?', (product_id(path),)).fetchone()
    return (200, public(row)) if row else (404, {'error': 'Producto no encontrado.'})

def register(routes):
    routes['GET', '/api/products'] = listing
    routes['GET', '/api/products/:id'] = detail
