# Ficha: ERP (operación en obra)

La parte original de BSynch: cuadrillas en obra, entrada/salida con PIN, horas, inventario, problemas de calidad y compras.

## Qué le pertenece
- Páginas: `/erp`, `/dashboard`, `/log`, `/timesheet`, `/inventory`, `/schedule`, `/settings` (ajustes del ERP), `/tablet` (kiosco), `/checkin/<…>`, `/qr-codes`, `/location`, `/sectionb`, `/issues-log`, `/issues/<…>`, `/unit-log/<…>`, `/unit-progress/<…>`, `/migrate`, `/lock/<…>`.
- API: `/api/workers*`, `/api/checkin*`, `/api/checkins`, `/api/active-checkins`, `/api/today-checkins`, `/api/auto-checkout`, `/api/attendance*`, `/api/safety-meeting*`, `/api/issues*`, `/api/qc*`, `/api/inventory*`, `/api/facturas*`, `/api/po*`, `/api/material-*`, `/api/suppliers*`, `/api/unit-materials*`, `/api/project-units*`, `/api/contacts*`, `/api/notifications*`, `/api/reports*`, `/api/ops-settings`, `/api/worker/*`, `/api/unit-sent`, `/api/sent-units`.
- Plantillas: `index`, `dashboard`, `log`, `timesheet`, `inventory`, `schedule`, `settings`, `tablet`, `checkin`, `qr_codes`, `location`, `sectionb`, `issues`, `issues_log`, `migrate`.
- Tablas: `workers`, `checkins`, `attendance_reports`, `safety_meetings`, `notifications`, `notification_reads`, `worker_location_history`, inventario, issues, compras, `unit_materials`, `project_units`, `contacts`, `sent_units`.
- Pruebas: crear `tests/test_erp.py` (las de PIN/check-in/tablet ya están en `test_security.py`, que es de Settings).

## Roles
`worker`, `lead`, `boss`, `admin` (reglas en `_ERP_ROLE_RULES`; las cambia Settings).

## Cómo está hoy
- Todas las pantallas piden sesión (modo `enforce`).
- PINs con hash; el PIN de un trabajador nuevo se muestra una sola vez.
- Tablet/kiosco: se bloquea tras 10 PINs malos y avisa al dueño; sin contraseña por defecto.
- Check-in manual por un admin queda con quién lo hizo y en hora de Texas (cambia sola con el horario de verano).
- `/api/auto-checkout` solo con la clave de cron.
- Se quitó el `mailto` del timesheet.

## Pruebas
- `tests/test_erp.py` (59 pruebas): sesión obligatoria, inventario (SKU, permisos, aviso de stock bajo), issues (pins, unir, estados), órdenes de compra (recibir parcial/total, asignar a obra, nunca stock negativo), solicitudes de material (aprobar, entregar, borrar devuelve stock), facturas de proveedor y horas del timesheet.

## Pendientes
- [ ] **ERP multi-empresa, paso 2 (lo hace esta conversación; Settings hizo el paso 1 el 2026-11-21).** Ya existe: columna `company` (texto, `not null`, índice) en las 22 tablas del ERP; todo lo anterior quedó como `'tdg'` (TDG Energy Services, del dueño). Default temporal `'tdg'` para que el código de hoy no se rompa. Registro `ERP_COMPANIES` (lee `contractor_companies` con `hubs` que incluyan `"erp"`; TDG siempre está). Empresa de prueba **`mbr` "MBR (Test)"** en **pausa** (reemplazó a `demo-erp`, pedido del dueño 2026-11-21).
  **ERP Home ya existe (Settings, 2026-11-21):** la tarjeta ERP de `/home` va a `/erp-hub`; el dueño ve las empresas ERP (TDG, MBR (Test)) y al abrir una queda en `session["erp_company"]` y entra a `/erp`. Los demás entran directo a la suya. **Usa `_erp_company()`** para saber la empresa de quien llama (ya resuelve: dueño = la que eligió; resto = su empresa; si no, TDG). Hoy solo TDG abre: cuando termines, pon `ERP_SEPARATED = True` en `app.py` y MBR (Test) se abre sola.
  Qué falta, en este orden:
  1. Usar `_erp_company()` en cada ruta (TDG para la gente del ERP de hoy; una empresa por persona; el dueño elige en ERP Home). Poner en la cabecera de `/erp` (`landing.html`) el nombre de la empresa y, para el dueño, un enlace "← ERP Home".
  2. Cada ruta del ERP (~88) **lee** con `&company=eq.<empresa>` y **guarda** con `company` puesta por el servidor (nunca la que mande la página).
  3. PIN de cuadrillas: único **por empresa** (hoy es único en toda la app); cada tablet de check-in amarrada a una empresa.
  4. Cambiar los ~23 textos fijos "TDG" / "Meridian Structural Group" por el nombre de la empresa (`ERP_COMPANIES`).
  5. Pruebas en `tests/test_erp.py`: una empresa no ve ni edita lo de otra, en cada función principal.
  6. Poner `ERP_SEPARATED = True` y avisar a Settings para: quitar el default `'tdg'`, pasar `mbr` a activa (y cargarle datos de ejemplo), abrir el ERP en `_saas_scope_guard` según los `hubs` de cada empresa y agregar `"erp"` a `SAAS_HUBS_READY`.
- [x] (Hecho por Settings, 2026-11-21) Fotos de issues y planos QC: el bucket `issue-photos` es privado; `/api/issues/upload-photo` y `/api/qc/upload-drawing` solo aceptan imágenes y devuelven `/api/issues/photo/<nombre>` (se sirve con sesión). Se quitó `/api/test-storage`. "Reset Pw" en `/settings` ahora manda un enlace en vez de escribir la clave de otro.
- [ ] **Para vender el ERP (pedido de Settings, 2026-11-14):** sus tablas (`workers`, `checkins`, `inventory_items`, `unit_issues`, `purchase_orders`, `material_requests`, `project_units`, `suppliers`, `daily_log`, etc.) no tienen columna de empresa. Hay que agregar `company` a cada una, filtrar por la empresa de quien llama en cada consulta y probar que una empresa no ve lo de otra. Cuando esté, Settings agrega `"erp"` a `SAAS_HUBS_READY`. Hoy los usuarios de empresas cliente tienen el ERP bloqueado en el servidor.
- [x] Escribir `tests/test_erp.py` con los flujos principales (inventario, issues, compras, timesheet).
- [ ] Revisar con el dueño qué pantallas siguen en uso y cuáles se pueden retirar.

## Riesgos encontrados (confirmados con pruebas, sin arreglar todavía)
1. ~~Inventario confía en el nombre que manda el navegador.~~ **Arreglado (14-nov-2026):** `_inventory_editor()` usa el usuario de la sesión (contraseña o el teclado de PIN de editor). Crear, editar, borrar, generar SKUs y aprobar solicitudes ya no leen `editor`/`approved_by` del cuerpo, y `created_by`/`updated_by`/`approved_by` se guardan con el nombre de la sesión. En el mismo cambio se quitó el `mailto` que mandaba el PIN nuevo en texto plano al correo del dueño (inventory, index, dashboard, issues_log).
2. ~~Borrados sin permiso ni auditoría.~~ **Arreglado (14-nov-2026), decisión del dueño: archivar, nunca borrar.** "Borrar" un issue, una factura o un artículo ahora pone `archived_at`, `archived_by` y `archive_reason`. El registro desaparece de las listas, queda en `_audit` (`erp.archive`) y un admin lo puede restaurar. Quién puede archivar: issues admin/boss/lead, facturas admin/boss, inventario los editores. Unir dos issues archiva el que se une (motivo "merged into …") en vez de borrarlo. Rutas nuevas, solo admin/boss: `GET /api/erp/archive/<issues|facturas|inventory>` y `POST /api/erp/archive/<tipo>/<id>/restore` (`erp.restore` en la auditoría). SQL: `migrations/erp_archive.sql`. Las listas filtran en Python, así que funcionan antes y después del SQL. Sin el SQL, archivar falla con un aviso claro y no borra nada.
   - **Segunda tanda (14-nov-2026):** también se archivan, nunca se borran, los proveedores (editores de inventario), los materiales por unidad (editores), las unidades del proyecto (admin/boss) y las solicitudes de material (admin/boss). Una solicitud **entregada** que se archiva devuelve su stock una sola vez (`stock_returned = true`, queda como goods receipt). Si se restaura, el stock se vuelve a descontar una sola vez (goods issue). Una solicitud archivada no se puede entregar.
   - Pendiente: falta una pantalla para ver y restaurar el archivo. Hoy solo existen las rutas de la API.
   - **Tercera tanda (14-nov-2026):** la asistencia (admin/boss/lead) y los contactos (admin/boss) se archivan. `/admin/wipe` ya no borra: copia cada fila de `daily_log` completa (JSON) a `daily_log_archive` y saca de `daily_log` solo las que se copiaron bien. Si la copia falla, se detiene y no saca nada. Queda en la auditoría como `erp.archive` / `daily_log:all`. Para recuperar un wipe hoy hay que usar SQL (los datos están en `daily_log_archive.data`); no hay botón.
   - Nota: el cierre automático de las 6:15 pm cuenta también la asistencia archivada al decidir a quién marcar ausente. Así, si se archivó un "ausente" equivocado, no se vuelve a crear solo.
   - Pendiente, otros borrados reales que quedan en el ERP: reuniones de seguridad (y su check-in del día), trabajadores inactivos (`/api/workers/inactive`) y por nombre, notificaciones, el registro de avance de una posición (`daily_log` al mover o borrar una posición) y fotos de issues en Storage. `unit_locks` es temporal y está bien que se borre.
3. ~~Entregar dos veces la misma solicitud descuenta el stock dos veces.~~ **Arreglado (14-nov-2026):** la entrega primero marca la solicitud como `Delivered` solo si no lo estaba (un único cambio en la base). Si ya estaba entregada responde 409 y no toca el stock, aunque sean dos toques seguidos o dos aparatos a la vez. Si la solicitud no existe, responde 404. `delivered_by` se guarda con el nombre de la sesión.
4. ~~`/api/po-test` ruta de depuración publicada.~~ **Quitada (14-nov-2026).**
5. Filtros que pasan el texto del usuario sin escapar a Supabase (`unit`, `status`, `limit`, `item_id`). Solo lectura, riesgo bajo. Escaparlos.
- Las reglas de rol (`_ERP_ROLE_RULES`) son de Settings: si se decide que solo admin borra, se le pide a esa conversación.

## Decisiones tomadas
- Ubicaciones de trabajadores: se borran solas a los 90 días. Nada más.
