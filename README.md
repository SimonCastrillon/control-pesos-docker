# control-pesos-docker

API para verificar lotes de producto por peso, construida con **Flask** y **PostgreSQL** en dos contenedores orquestados con **Docker Compose**.

La API recibe los pesos de una muestra, determina si el lote es conforme, guarda el resultado en PostgreSQL y permite consultar el historial. La API se comunica con la base de datos por el **nombre del servicio** (`db`) dentro de una red propia de Docker, nunca por `localhost` ni por una IP fija.

> **Nota:** el criterio de conformidad es didáctico. No reproduce ninguna norma metrológica.

---

## Estructura del repositorio

```
control-pesos-docker/
├── .github/workflows/ci.yml   # CI: pruebas, construcción de imágenes e integración
├── docker-compose.yml         # servicios api y db, red, volumen y variables
├── .env.example               # plantilla de variables (el .env real NO se sube)
├── .gitattributes
├── .gitignore
├── README.md
└── api/
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt       # dependencias de producción
    ├── requirements-dev.txt   # pytest (pruebas unitarias)
    ├── src/
    │   ├── __init__.py
    │   ├── app.py             # endpoints HTTP (Flask)
    │   ├── logica.py          # reglas de verificación (sin dependencias externas)
    │   └── db.py              # conexión y consultas a PostgreSQL
    └── tests/
        ├── __init__.py
        └── test_logica.py
```

---

## Requisitos

- [Docker Desktop](https://docs.docker.com/desktop/) abierto, con el motor en estado *Engine running*.
- Git.
- Python 3.12 o superior, solo para correr las pruebas sin Docker (opcional).

---

## 1. Configuración

Clona el repositorio:

```bash
git clone https://github.com/SimonCastrillon/control-pesos-docker.git
cd control-pesos-docker
```

Crea el archivo `.env` a partir de la plantilla.

**Windows (CMD o PowerShell):**

```bat
copy .env.example .env
```

**Linux / Mac / Git Bash:**

```bash
cp .env.example .env
```

Edita `.env` y cambia la contraseña:

```env
POSTGRES_DB=control_pesos
POSTGRES_USER=calidad
POSTGRES_PASSWORD=cambia-esta-clave
```

---

## 2. Levantar los contenedores

```bash
docker compose up --build
```

La primera vez descarga las imágenes base y construye la API. El servicio `api` espera a que `db` esté sano (`healthcheck`) antes de arrancar.

Verificar que ambos contenedores están corriendo (en otra terminal):

```bash
docker ps
```

---

## 3. Probar la API

### Endpoints

|Método|Ruta|Descripción|¿Usa la BD?|
|-|-|-|-|
|GET|`/salud`|Estado de la API|No|
|GET|`/salud/db`|Verifica la conexión con el servicio `db`|Sí|
|POST|`/verificaciones`|Verifica un lote y guarda el resultado|Sí (escribe)|
|GET|`/verificaciones`|Lista las verificaciones guardadas|Sí (lee)|

### Prueba de comunicación (ida y vuelta)

**Windows (CMD):**

```bat
curl http://localhost:8000/salud
curl http://localhost:8000/salud/db

curl -X POST http://localhost:8000/verificaciones -H "Content-Type: application/json" -d "{\"lote\":\"L-001\",\"pesos\":[500.5,501.0,499.8,500.9],\"nominal\":500,\"tolerancia\":15}"

curl http://localhost:8000/verificaciones
```

**Windows (PowerShell):**

```powershell
Invoke-RestMethod http://localhost:8000/salud/db

Invoke-RestMethod -Method Post -Uri http://localhost:8000/verificaciones `
  -ContentType "application/json" `
  -Body '{"lote":"L-001","pesos":[500.5,501.0,499.8,500.9],"nominal":500,"tolerancia":15}'

Invoke-RestMethod http://localhost:8000/verificaciones
```

**Linux / Mac / Git Bash:**

```bash
curl -X POST http://localhost:8000/verificaciones \
  -H "Content-Type: application/json" \
  -d '{"lote":"L-001","pesos":[500.5,501.0,499.8,500.9],"nominal":500,"tolerancia":15}'

curl http://localhost:8000/verificaciones
```

Respuesta esperada del `POST` (código 201; el `id` depende de los registros ya guardados):

```json
{
  "conforme": true,
  "id": 1,
  "limite_inferior": 485.0,
  "n": 4,
  "promedio": 500.55,
  "unidades_defectuosas": 0
}
```

El `GET /verificaciones` debe incluir ese registro, con su `lote` y su fecha `creado_en` (`limite_inferior` no se guarda). Esto demuestra que la API escribió en `db` y luego leyó desde `db`.

### Criterio de verificación

* **Límite inferior** = nominal − tolerancia.
* **Unidades defectuosas** = unidades con peso menor al límite inferior.
* El lote es **conforme** si el promedio ≥ nominal **y** no hay unidades defectuosas.

---

## 4. Evidencias de red y datos

Ver la red propia y los dos contenedores conectados a ella:

```bash
docker network inspect red-app
```

Consultar los datos directamente en PostgreSQL (con los valores de tu `.env`):

```bash
docker compose exec db psql -U calidad -d control_pesos -c "SELECT * FROM verificaciones;"
```

Ver el volumen donde persisten los datos:

```bash
docker volume ls
```

---

## 5. Apagar

Detener y eliminar los contenedores (los datos se conservan en el volumen):

```bash
docker compose down
```

Detener los contenedores y además eliminar el volumen y **TODOS** los datos:

```bash
docker compose down -v
```

---

## 6. Pruebas unitarias (sin Docker)

**Windows (CMD):**

```bat
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -v
```

**Windows (PowerShell):**

```powershell
cd api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -v
```

**Linux / Mac:**

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

---

## 7. Integración continua (GitHub Actions)

El workflow `.github/workflows/ci.yml` se ejecuta en cada **push** y en cada **pull request** a `main`:

1. **pruebas**: con Python 3.12 instala `api/requirements-dev.txt` y ejecuta `pytest -v` en `api/`.
2. **build**: solo corre si las pruebas pasan. Crea el `.env` desde `.env.example`, construye las imágenes con `docker compose build` y hace una prueba de integración:
   * levanta los servicios con `docker compose up -d --wait`;
   * consulta `/salud/db`;
   * guarda el lote `CI-001` con un `POST` a `/verificaciones`;
   * confirma con un `GET` que `CI-001` aparece en el historial.

   Si algo falla, muestra `docker compose logs`. Al final siempre limpia el entorno de CI con `docker compose down -v`.

El resultado se ve en la pestaña **Actions** del repositorio. Un check verde indica que las pruebas pasaron, las imágenes se construyeron sin errores y la API guardó y leyó datos en PostgreSQL.

---

## 8. Seguridad y buenas prácticas

* Las credenciales viven solo en `.env`, que está en `.gitignore`. El repositorio incluye `.env.example` como plantilla, sin valores reales.
* El código no contiene contraseñas: las lee de variables de entorno.
* `api/.dockerignore` excluye de la imagen cachés, entornos virtuales, pruebas, dependencias de desarrollo y el `.env`.
* Las imágenes base usan versiones fijas (`python:3.12-slim`, `postgres:16-alpine`), no `latest`.
* La API corre en el contenedor con un usuario sin privilegios.
* El puerto de PostgreSQL no se expone al host: solo la API puede alcanzarlo dentro de la red `red-app`.

---

## Autor

Simon Esteban Castrillon Martinez · Integración continua · Politecnico Grancolombiano · 2026
