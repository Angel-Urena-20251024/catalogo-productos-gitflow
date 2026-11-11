"""Búsqueda de productos por nombre sin interpretar comodines SQL."""
from app import connection, public

def search(path, query, body):
    text = query.get('q', [''])[0].strip()
    if len(text) > 100:
        return 400, {'error': 'La búsqueda no puede superar 100 caracteres.'}
    with connection() as db:
        rows = db.execute('SELECT * FROM products WHERE instr(lower(name),lower(?))>0 ORDER BY id DESC', (text,)).fetchall()
    return 200, [public(row) for row in rows]

def register(routes):
    routes['GET', '/api/search'] = search
