# Catálogo de productos

CRUD web de productos para la práctica de Git y Git Flow de Programación III.
Permite registrar, consultar, editar, eliminar y buscar productos. Conserva los datos en SQLite.

## Ejecutar

Requiere **Python 3.10 o posterior**. No necesita instalar paquetes externos.

```sh
python3 app.py
```

Abrir http://127.0.0.1:8000. La base `catalogo.db` se crea al iniciar y queda excluida del control de versiones.
En Windows puede utilizarse `py app.py`. Para otro puerto, definir la variable `PORT`.
Este servidor está destinado a demostraciones locales; no ofrece autenticación ni despliegue público.

## Uso

1. Completar nombre, precio (hasta dos decimales) y existencias enteras.
2. Guardar y comprobar que el producto aparece en la tabla.
3. Pulsar **Editar**, modificar un valor y guardar.
4. Buscar por una parte del nombre; **Todos** recupera la lista completa.
5. Pulsar **Eliminar** y confirmar la operación.
6. Reiniciar el servidor y comprobar la persistencia de los registros restantes.

## Ramas de trabajo

- `feature/listar-productos`: lista y detalle por identificador.
- `feature/crear-productos`: registro y validación del lado del servidor.
- `feature/editar-productos`: actualización y tratamiento de identificadores inexistentes.
- `feature/eliminar-productos`: eliminación por identificador y confirmación en pantalla.
- `feature/buscar-productos`: búsqueda por nombre mediante consultas parametrizadas.

La práctica exige tres PR por cada rama: hacia `dev`, `qa` y `main`.
Es una adaptación académica del modelo Git Flow. Cada función se comprueba antes de integrar su PR en el siguiente destino.
Los quince PR y su estado deben verificarse en GitHub; la existencia de este README no acredita que ya se hayan realizado.

## Pruebas

```sh
python3 -m unittest -v test_app.py
```

Las pruebas utilizan una base temporal y verifican HTTP, CRUD, validación, búsqueda, persistencia y recursos inexistentes.
No se requieren datos personales ni credenciales para probar la aplicación.

## API

| Método | Recurso | Operación |
| --- | --- | --- |
| GET | `/api/products` | Listar |
| GET | `/api/products/ID` | Consultar detalle |
| POST | `/api/products` | Crear |
| PUT | `/api/products/ID` | Editar |
| DELETE | `/api/products/ID` | Eliminar |
| GET | `/api/search?q=texto` | Buscar |

POST y PUT reciben JSON: `{"name":"Cuaderno","price":"150.00","stock":10}`.
Los precios se guardan en centavos enteros para evitar errores de representación binaria en los datos persistidos.
