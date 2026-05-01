# Abuela Empanadas API

Sistema de gestion para "Abuela Empanadas" construido con FastAPI, SQLAlchemy async, Pydantic v2 y PostgreSQL.

## Estado del Proyecto

### Implementado

- Estructura base de FastAPI organizada por capas: endpoints, modelos, esquemas, servicios, base de datos y configuracion.
- Configuracion de Alembic para migraciones de base de datos.
- Migracion inicial disponible en `alembic/versions/`.
- Modelos SQLAlchemy definidos: `Usuario`, `Sucursal`, `Producto`, `Factura`, `FacturaDetalle`, `Anulacion`, `CierreDiario`, `Egreso`, `Proveedor`, `Insumo` y `Stock`.
- Esquemas Pydantic para validacion y serializacion de datos.
- Autenticacion con JWT y bcrypt.
- Endpoints API bajo el prefijo `/api/v1`.
- Pruebas automatizadas en `tests/`.
- Workflow de GitHub Actions para linting, tests con coverage, escaneo de seguridad, build y despliegues.

### Pendiente o en revision

- Revisar endpoints incompletos o duplicados antes de considerar la API estable.
- Confirmar el estado de migraciones aplicadas directamente en la base de datos de cada ambiente.
- Completar documentacion de payloads y ejemplos de respuesta por endpoint.

## Tecnologias

- **Framework:** FastAPI
- **ORM:** SQLAlchemy async
- **Base de datos:** PostgreSQL configurable mediante `DATABASE_URL`
- **Migraciones:** Alembic
- **Autenticacion:** JWT + bcrypt
- **Validacion:** Pydantic v2
- **Testing:** pytest, pytest-asyncio, httpx
- **CI/CD:** GitHub Actions

## Configuracion

1. Activar entorno virtual:

   ```powershell
   venv\Scripts\activate
   ```

2. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno usando `.env.example` como referencia.

4. Ejecutar migraciones:

   ```powershell
   alembic upgrade head
   ```

5. Iniciar servidor de desarrollo:

   ```powershell
   fastapi dev main.py
   ```

La aplicacion queda disponible por defecto en `http://127.0.0.1:8000`.

## Estructura de Carpetas

```txt
abuela_empanadas_api/
├── app/
│   ├── api/v1/endpoints/  # Endpoints API
│   ├── core/              # Configuracion, seguridad y dependencias
│   ├── db/                # Sesion y conexion a base de datos
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   └── services/          # Logica de negocio
├── alembic/               # Migraciones
├── tests/                 # Pruebas automatizadas
├── .github/workflows/     # Workflows CI/CD
├── main.py                # Punto de entrada local
└── requirements.txt
```

## Tablas en Base de Datos

- `usuarios`
- `sucursales`
- `productos`
- `facturas`
- `factura_detalles`
- `anulaciones`
- `cierres_diarios`
- `egresos`
- `proveedores`
- `insumos`
- `stocks`

## API Endpoints

### Salud

- `GET /health` - Verifica que la aplicacion responde.

### Autenticacion

- `POST /api/v1/auth/login` - Genera token de acceso.
- `GET /api/v1/auth/me` - Devuelve el usuario autenticado.
- `POST /api/v1/auth/logout` - Cierra sesion a nivel de cliente.

### Recursos

- `GET /api/v1/usuarios/` - Lista usuarios.
- `POST /api/v1/usuarios/` - Crea usuario.
- `GET /api/v1/sucursales/` - Lista sucursales.
- `POST /api/v1/sucursales/` - Crea sucursal.
- `GET /api/v1/productos/` - Lista productos.
- `POST /api/v1/productos/` - Crea producto.
- `GET /api/v1/facturas/` - Lista facturas.
- `POST /api/v1/facturas/` - Crea factura.
- `GET /api/v1/facturas/anuladas` - Lista anulaciones de facturas.
- `POST /api/v1/facturas/{factura_id}/anular` - Anula una factura.
- `GET /api/v1/cierres/` - Lista cierres diarios.
- `POST /api/v1/cierres/` - Crea cierre diario.
- `GET /api/v1/gastos/` - Lista egresos o gastos.
- `POST /api/v1/gastos/` - Crea egreso o gasto.
- `GET /api/v1/proveedores/` - Lista proveedores.
- `POST /api/v1/proveedores/` - Crea proveedor.
- `GET /api/v1/insumos/` - Lista insumos.
- `POST /api/v1/insumos/` - Crea insumo.
- `GET /api/v1/reportes/` - Consulta reportes.

## CI/CD

El proyecto incluye un workflow de GitHub Actions en `.github/workflows/ci.yml` con:

- Matriz de Python `3.9`, `3.10` y `3.11`.
- Instalacion de dependencias.
- Linting.
- Pruebas con coverage.
- Escaneo de seguridad con Bandit.
- Build de aplicacion e imagen Docker.
- Jobs de despliegue para staging y produccion.
