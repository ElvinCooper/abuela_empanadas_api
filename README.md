# Abuela Empanadas API

Sistema de gestión para "Abuela Empanadas" construido con FastAPI y PostgreSQL.

## Estado del Proyecto

### ✅ Completado

- Estructura completa del proyecto (FastAPI, SQLAlchemy async, Pydantic).
- Configuración de Alembic para migraciones de base de datos.
- Migración inicial aplicada exitosamente.
- Modelos SQLAlchemy definidos: `Usuario`, `Sucursal`, `Producto`, `Factura`, `FacturaDetalle`, `Anulacion`, `CierreDiario`, `Egreso`, `Proveedor`, `Insumo`, `Stock`.
- Esquemas Pydantic para validación de datos.
- Servicios base para autenticación y lógica de negocio.
- Endpoints API con autenticación JWT.
- Repositorio inicializado en GitHub.

### 🛠️ Tecnologías

- **Framework:** FastAPI
- **ORM:** SQLAlchemy (async)
- **Base de Datos:** PostgreSQL (Neon)
- **Migraciones:** Alembic
- **Autenticación:** JWT + bcrypt
- **Validación:** Pydantic v2

## Configuración

1. Activar entorno virtual: `venv\Scripts\activate`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables en `.env` (ver `.env.example`)
4. Ejecutar migraciones: `alembic upgrade head`
5. Iniciar servidor: `fastapi dev main.py`

## Estructura de Carpetas

```txt
abuela_empanadas_api/
├── app/
│   ├── api/v1/endpoints/  # Endpoints API
│   ├── core/               # Configuración y seguridad
│   ├── db/                 # Conexión a BD
│   ├── models/             # Modelos SQLAlchemy
│   ├── schemas/            # Esquemas Pydantic
│   └── services/           # Lógica de negocio
├── alembic/              # Migraciones
├── tests/                # Pruebas
└── requirements.txt
```

## Tablas en Base de Datos

- usuarios
- sucursales
- productos
- facturas
- factura_detalles
- anulaciones
- cierres_diarios
- egresos
- proveedores
- insumos
- stocks

## API Endpoints

- `/v1/auth/login` - Autenticación
- `/v1/usuarios/` - Gestión de usuarios
- `/v1/sucursales/` - Gestión de sucursales
- `/v1/productos/` - Gestión de productos
- `/v1/facturas/` - Gestión de facturas
- `/v1/anulaciones/` - Anulaciones
- `/v1/cierres/` - Cierres diarios
- `/v1/egresos/` - Egresos
- `/v1/proveedores/` - Proveedores
- `/v1/insumos/` - Insumos
- `/v1/reportes/` - Reportes
