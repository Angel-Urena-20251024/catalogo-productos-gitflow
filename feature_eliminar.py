"""Eliminación explícita por identificador."""
from app import connection, product_id

def delete(path, query, body):
    with connection() as db:
        result = db.execute('DELETE FROM products WHERE id=?', (product_id(path),))
    return (200, {'message': 'Producto eliminado.'}) if result.rowcount else (404, {'error': 'Producto no encontrado.'})

def register(routes):
    routes['DELETE', '/api/products/:id'] = delete
