"""Servidor local del catálogo. Python 3.10+; solo biblioteca estándar."""
import importlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('CATALOGO_DB', ROOT / 'catalogo.db'))
ROUTES = {}

def connection():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    with connection() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS products (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>=0),
          stock INTEGER NOT NULL CHECK(stock>=0))''')

def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Se espera un objeto con nombre, precio y existencias.')
    name = data.get('name')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
        raise ValueError('El nombre debe tener entre 1 y 100 caracteres.')
    try:
        price = Decimal(str(data.get('price')))
        if not price.is_finite() or price < 0 or price > 9999999 or price.as_tuple().exponent < -2:
            raise ValueError()
    except (InvalidOperation, ValueError):
        raise ValueError('El precio debe ser positivo o cero y tener como máximo dos decimales.')
    stock = data.get('stock')
    if isinstance(stock, bool) or not isinstance(stock, int) or not 0 <= stock <= 1000000:
        raise ValueError('Las existencias deben ser un entero entre 0 y 1000000.')
    return name.strip(), int(price * 100), stock

def public(row):
    return dict(id=row['id'], name=row['name'], price=f"{row['price_cents']/100:.2f}", stock=row['stock'])

def product_id(path):
    try:
        value = int(path.rsplit('/', 1)[-1])
        if value <= 0: raise ValueError()
        return value
    except ValueError:
        raise ValueError('El identificador del producto no es válido.')

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def dispatch(self):
        parsed = urlparse(self.path)
        if self.command == 'GET' and parsed.path == '/':
            data = (ROOT / 'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        body = None
        try:
            if self.command in ('POST', 'PUT'):
                if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    self.reply(415, {'error': 'Se requiere application/json.'}); return
                size = int(self.headers.get('Content-Length', '0'))
                if size <= 0 or size > 8192:
                    self.reply(400, {'error': 'El cuerpo de la solicitud no es válido.'}); return
                body = json.loads(self.rfile.read(size))
            key = parsed.path
            if key.startswith('/api/products/'):
                key = '/api/products/:id'
            route = ROUTES.get((self.command, key))
            if route is None:
                self.reply(404, {'error': 'Recurso no encontrado.'}); return
            status, data = route(parsed.path, parse_qs(parsed.query), body)
            self.reply(status, data)
        except (ValueError, json.JSONDecodeError):
            self.reply(400, {'error': 'Datos inválidos: revise nombre, precio y existencias.'})
        except sqlite3.Error:
            self.reply(500, {'error': 'No fue posible completar la operación.'})

    do_GET = do_POST = do_PUT = do_DELETE = dispatch

if __name__ == '__main__':
    sys.modules['app'] = sys.modules[__name__]

for module in sorted(ROOT.glob('feature_*.py')):
    importlib.import_module(module.stem).register(ROUTES)

if __name__ == '__main__':
    initialize()
    port = int(os.environ.get('PORT', '8000'))
    print(f'Catálogo disponible en http://127.0.0.1:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
