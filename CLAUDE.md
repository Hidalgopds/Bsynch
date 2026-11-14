# BSynch: manual para Claude

Léelo completo antes de tocar nada. Después lee la ficha de tu sección en `docs/areas/`.

## Cómo hablar con el dueño
- Responde **en español**, simple y corto. Él escribe rápido, desde el teléfono y a veces con errores: entiende la intención.
- Nada de jerga técnica sin explicarla. Di qué cambió, cómo se ve en la app y qué tiene que hacer él (si algo).
- Si una decisión es suya (precio, diseño, borrar datos), pregunta. Si es técnica y obvia, decide y avisa.

## Qué es BSynch
Una app web (Flask, un solo archivo grande `app.py` + `templates/` + `static/`) con 5 secciones, las mismas tarjetas de `/home`:

| Sección | Para qué | Ficha |
|---|---|---|
| ERP | Operación en obra: cuadrillas, PIN, check-in, timesheets, inventario, issues, órdenes de compra | `docs/areas/erp.md` |
| Contractor | Contratistas (Hicons, Bsynch): proyectos, órdenes de trabajo, clientes, estimados, facturas | `docs/areas/contractor.md` |
| Marketing | Campañas y leads. Hoy vacía ("coming soon") | `docs/areas/marketing.md` |
| Home Lab (Family Hub) | Familia: checklist de niños, juegos, Hermaniland | `docs/areas/homelab.md` |
| Settings | **Todo lo común**: login, usuarios y roles, empresas, seguridad, legal, pruebas, despliegue, cobros | `docs/areas/settings.md` |

**Settings manda sobre lo común.** Las demás secciones no cambian login, sesiones, roles, cabeceras de seguridad, `_audit`, límites de intentos, `sb_url()/sb_headers()`, migraciones de tablas compartidas ni este archivo. Si lo necesitan, lo dicen y lo hace la conversación de Settings.

## Dónde corre
- Servidor: **Render**, se despliega solo desde la rama `main` de GitHub (`Hidalgopds/Bsynch`). Gunicorn 1 worker, 4 hilos.
- Base de datos: **Supabase** producción: `wanfpiogchwttsippekm` (principal) y `fhkfpqgfzegqcyajvjlo` (empresa cliente NNC). Staging para pruebas de carga: `yxlambgifwcmkmzxoosm` (único lugar donde se permite cargar datos falsos).
- El servidor habla con Supabase por REST con la clave de servicio. **RLS activo en todas las tablas y sin políticas**: solo el servidor lee y escribe. Nunca mandes una clave de Supabase al navegador.
- Multi-empresa por subdominio (`<empresa>.bsynch.com`) con la tabla `bsynch_companies`.

## Cómo trabajar (varias conversaciones a la vez)
Hay una conversación por sección trabajando en paralelo sobre el mismo repositorio. Para no pisarse:
1. **Antes de empezar** y **antes de subir**: `git fetch origin main && git rebase origin/main` (o `git pull --rebase origin main`).
2. Trabaja en tu rama de la sesión. Toca solo los archivos de tu sección (lista en tu ficha). En `app.py`, solo el bloque de tu sección.
3. Corre las pruebas: `python tests/run_all.py`. **No se publica con pruebas fallando.** Si agregas algo importante, agrega su prueba en `tests/test_<sección>.py`.
4. Para publicar: `git push origin <tu-rama>:main` (Render despliega solo). Si el push falla porque `main` avanzó, vuelve al paso 1, corre pruebas y reintenta. Nunca `--force` a `main`.
5. Commits con mensaje claro de qué y por qué. Termina el mensaje con las líneas de atribución que indique la sesión.
6. Cambios de base de datos: SQL en `migrations/` (idempotente: `if not exists`), aplicado a producción con cuidado, y después revisar los Security Advisors de Supabase (cero ERROR). Tabla nueva = `enable row level security` y sin políticas.
7. Al terminar algo, actualiza **tu ficha** (`docs/areas/<sección>.md`): qué se hizo, decisiones y pendientes.

## Reglas que no se rompen
- **Nunca borrar datos de negocio**: facturas, órdenes, fotos, recibos, contactos, registros. Lo único que se borra solo son las **ubicaciones de más de 90 días** (`_retention_purge`). El `audit_log` **nunca** se borra.
- **Nunca secretos** (claves, contraseñas, tokens) en el código, en el chat, en commits ni en capturas. Viven solo en las variables de entorno de Render. El repositorio es **público** mientras el dueño no lo pase a privado.
- **No pongas el correo personal del dueño** ni datos de clientes reales en el repo o en pruebas. En pruebas usa `@example.com`.
- **Nunca pruebas de carga contra producción** (`bsynch.com`). Solo staging (ver `loadtest/README.md`).
- Permisos siempre en el servidor, no solo escondiendo botones. Cada empresa ve solo lo suyo.
- Todo lo sensible pasa por `_audit(...)` (inicios de sesión, cambios de rol, PIN, configuración, empresas).
- Contraseñas con bcrypt; PINs con `_pin_hash` (prefijo `h1:`); nunca devolverlos en una respuesta.
- Formularios públicos: honeypot `website` + límite por IP (`_PUBLIC_FORMS`).
- Accesibilidad: contraste AA (teal `#0f766e`, gris `#566275`), botones con texto o `aria-label`.

## Pruebas
- `python tests/run_all.py` corre todo. Usan un **Supabase falso en memoria** (`tests/harness.py`): no tocan internet ni la base real.
- Personas de prueba: Hana (Manager de Hicons), Mia (User de Hicons), Bob (Leader de Bsynch), Newbie (sin empresa), `owner@example.com` (dueño de la plataforma), Crew One (PIN 4821) y Crew New (sin PIN). Contraseña = `pw-` + nombre en minúsculas.
- Helpers: `get(path, user)`, `send(method, path, user, body)`, `check(nombre, condición)`, `DB` (las tablas), `MAIL` (correos que la app intentó mandar).
- Dependencias: `python -m pip install -r requirements.txt`.

## Documentos útiles
- `docs/security/`: política de seguridad, plan de incidentes, proveedores, riesgos y controles (ISO 27001/27701, SOC 2).
- `loadtest/`: pruebas de carga con k6 contra staging.
- `migrations/`: SQL de la base de datos.
