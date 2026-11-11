import json
import tempfile
import unittest
from pathlib import Path
import app

class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        app.DB = Path(cls.temp.name) / 'test.db'
        app.initialize()
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def setUp(self):
        with app.connection() as db: db.execute('DELETE FROM products')
    def request(self, method, path, body=None):
        from io import BytesIO
        from types import SimpleNamespace
        from http.client import HTTPResponse
        payload=b'' if body is None else json.dumps(body).encode()
        request=(f'{method} {path} HTTP/1.0\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: {len(payload)}\r\n\r\n').encode()+payload
        wire=SimpleNamespace(input=BytesIO(request), output=BytesIO())
        class TestHandler(app.Handler):
            def setup(self):
                self.rfile=self.request.input; self.wfile=self.request.output
            def finish(self): pass
            def log_message(self, *args): pass
        TestHandler(wire, ('127.0.0.1', 0), None)
        class ResponseSocket:
            def makefile(self, *args): return BytesIO(wire.output.getvalue())
        response=HTTPResponse(ResponseSocket()); response.begin()
        raw=response.read()
        return response.status, raw if path=='/' else json.loads(raw)
    def create(self, name='Cuaderno'):
        status,p=self.request('POST','/api/products',{'name':name,'price':'150.25','stock':10})
        self.assertEqual(status,201); return p
    def test_crud_complete(self):
        p=self.create(); path='/api/products/'+str(p['id'])
        self.assertEqual(self.request('GET',path),(200,p))
        self.assertEqual(len(self.request('GET','/api/products')[1]),1)
        status,edited=self.request('PUT',path,{'name':'Libreta','price':'175.50','stock':8})
        self.assertEqual((status,edited['name'],edited['price'],edited['stock']),(200,'Libreta','175.50',8))
        self.assertEqual(self.request('DELETE',path)[0],200)
        self.assertEqual(self.request('GET',path)[0],404)
    def test_invalid_products(self):
        for body in [None,[],{'name':' ','price':'1','stock':1},{'name':'A','price':'-1','stock':1},{'name':'A','price':'NaN','stock':1},{'name':'A','price':'1.123','stock':1},{'name':'A','price':'1','stock':1.5},{'name':'A','price':'1','stock':True}]:
            with self.subTest(body=body): self.assertEqual(self.request('POST','/api/products',body)[0],400)
    def test_search_and_literal_sql(self):
        self.create('Cuaderno'); self.create('Lápiz')
        status,rows=self.request('GET','/api/search?q=CUADER')
        self.assertEqual(status,200); self.assertEqual([r['name'] for r in rows],['Cuaderno'])
        self.assertEqual(self.request('GET','/api/search?q=%25')[1],[])
        self.assertEqual(self.request('GET','/api/search?q=%27%20OR%201%3D1--')[1],[])
    def test_missing_and_bad_identifiers(self):
        for method in ['GET','DELETE','PUT']:
            body={'name':'A','price':'1','stock':1} if method=='PUT' else None
            self.assertEqual(self.request(method,'/api/products/9999',body)[0],404)
            self.assertEqual(self.request(method,'/api/products/no',body)[0],400)
    def test_persistence_and_money(self):
        self.create(); app.initialize()
        with app.connection() as db: self.assertEqual(db.execute('SELECT price_cents FROM products').fetchone()[0],15025)
    def test_page(self):
        status,html=self.request('GET','/'); self.assertEqual(status,200); self.assertIn(b'Cat',html)

if __name__=='__main__':unittest.main()
