# Pruebas de carga (k6) y entorno de staging

Las pruebas de carga simulan muchas personas usando BSynch a la vez para saber cuántas aguanta antes de ponerse lenta o fallar. **Siempre en staging, nunca en producción.** El script se niega a correr contra `bsynch.com`, porque en producción la prueba:
- afectaría a Renee, Maria y los demás;
- activaría el bloqueo por intentos y las alertas de seguridad;
- podría mandar correos de verdad.

## ¿Es seguro usar k6?
- k6 es de Grafana Labs, de código abierto (licencia AGPL-3.0). Usarlo para probar no obliga a nada; la licencia solo aplica si lo modificas y lo distribuyes.
- **No se instala dentro de la app:** corre desde tu computadora y le hace peticiones a staging, como un navegador. En BSynch no queda nada de k6, solo este script.
- Instálalo solo desde fuentes oficiales: `winget install k6 --source winget` (Windows), `brew install k6` (Mac) o los releases de github.com/grafana/k6. Verifica con `k6 version`. Probado con **v1.8.2**.
- Las contraseñas de prueba **nunca** van en el script ni en el repositorio: se pasan al momento de correrlo.
- El script es de **solo lectura**: entra, abre órdenes, fotos, calendario y facturación. No crea, no envía y no borra nada.

## 1. Base de datos de staging (Supabase)
Ya existe un proyecto separado: **bsynch-staging** (`yxlambgifwcmkmzxoosm`, us-east-1, plan gratis).
1. Estructura (las mismas tablas que producción, sin ningún dato):
   - En Supabase → **producción** → SQL Editor, corre `loadtest/export_schema.sql`. Solo lee la estructura; no toca ni lee datos.
   - Copia el resultado (columna `ddl`), y en Supabase → **staging** → SQL Editor pégalo y córrelo.
   - (Si me reconecto a Supabase, este paso lo hago yo.)
2. Datos falsos, desde tu computadora:
   ```
   pip install requests bcrypt pillow
   set STAGING_SUPABASE_URL=https://yxlambgifwcmkmzxoosm.supabase.co
   set STAGING_SERVICE_KEY=<staging → Project Settings → API keys → service_role>
   python loadtest/seed_staging.py --jobs 300 --users 5
   ```
   Crea 300 órdenes, 120 fotos de tamaño real, 3 carpetas de clientes, 40 clientes y 5 cuentas de prueba (`loadtest1` es Manager). Al final imprime las contraseñas, que son nuevas en cada corrida: guárdalas tú, no en el repositorio. El script se niega a correr contra la base de producción.

## 2. Servidor de staging (Render)
Render → New → Web Service → el mismo repositorio, rama `main`.
- **Nombre:** `bsynch-staging` (su dirección será `https://bsynch-staging.onrender.com`).
- **Plan:** el **mismo que producción**, para que los resultados sirvan. Render cobra por el tiempo de uso; suspende el servicio al terminar.
- **Start command:** `gunicorn app:app --workers=1 --threads=4` (igual que el Procfile).
- **Variables de entorno**, solo estas:

| Variable | Valor |
|---|---|
| `SUPABASE_URL` | `https://yxlambgifwcmkmzxoosm.supabase.co` |
| `SUPABASE_KEY` | la service_role key **de staging** |
| `SECRET_KEY` | un texto largo al azar (distinto al de producción) |
| `ERP_AUTH_MODE` | `enforce` |
| `CT_SCHEDULER` | `0` (sin correos diarios ni reportes) |

**No pongas** `RESEND_API_KEY`, `SMTP_*`, `CONTRACTOR_SMTP_*` ni `ANTHROPIC_API_KEY`. Así staging no puede mandar correos ni gastar IA aunque algo lo intente.

## 3. Correr las pruebas
De menor a mayor, y mirando los resultados entre una y otra:
```
k6 run -e BASE_URL=https://bsynch-staging.onrender.com -e LT_USERS="loadtest1:CLAVE,loadtest2:CLAVE" -e MANAGER=1 -e PROFILE=smoke  loadtest/bsynch-load.js
k6 run ... -e PROFILE=load   loadtest/bsynch-load.js     # hasta 50 personas a la vez, 6 min
k6 run ... -e PROFILE=stress loadtest/bsynch-load.js     # hasta 100 personas, 6 min
k6 run ... -e PROFILE=spike  loadtest/bsynch-load.js     # de 5 a 80 de golpe
```
Cada persona simulada abre Work orders, entra a una orden (pasos y fotos), mira el calendario y, con `MANAGER=1`, facturación y dashboard, con pausas de 1 a 3 segundos como una persona real.

## 4. Cómo leer el resultado
Al final, k6 imprime un resumen y guarda el detalle en `loadtest/last-summary.json` (no se sube al repositorio).

| Métrica | Bien | Revisar |
|---|---|---|
| errores | menos de 1 % | más de 1 % |
| 95 % de peticiones | menos de 0.8 s | más de 0.8 s |
| abrir Work orders (95 %) | menos de 1.5 s | más de 1.5 s |

Si una meta no se cumple, k6 termina con error y dice cuál. Mándame el `last-summary.json` y lo analizamos. Las causas típicas son: pocos procesos en Render (se sube `--workers`), consultas lentas a Supabase (índices) o fotos pesadas (moverlas a Storage).

## 5. Al terminar
- Suspende el servicio de staging en Render.
- En Supabase puedes pausar el proyecto de staging.
- Las cuentas `loadtest*` solo existen en staging.

## Prueba local (ya hecha)
El script se validó contra una copia local de la app con datos en memoria: 80 personas a la vez, 9,285 peticiones, 0 % de errores, y el 95 % en menos de 11 ms. Eso solo mide el código de la app; la base de datos real y el servidor de Render se miden en staging.
