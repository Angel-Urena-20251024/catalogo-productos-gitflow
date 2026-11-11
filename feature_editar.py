"""Actualización de un producto existente."""
from app import connection, validate, public, product_id

def update(path, query, body):
    values = validate(body)
    ident = product_id(path)
    with connection() as db:
        result = db.execute('UPDATE products SET name=?,price_cents=?,stock=? WHERE id=?', (*values, ident))
        if not result.rowcount:
            return 404, {'error': 'Producto no encontrado.'}
        row = db.execute('SELECT * FROM products WHERE id=?', (ident,)).fetchone()
    return 200, public(row)

def register(routes):
    routes['PUT', '/api/products/:id'] = update
