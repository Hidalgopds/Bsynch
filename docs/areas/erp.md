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
- [x] Escribir `tests/test_erp.py` con los flujos principales (inventario, issues, compras, timesheet).
- [ ] Revisar con el dueño qué pantallas siguen en uso y cuáles se pueden retirar.

## Riesgos encontrados (confirmados con pruebas, sin arreglar todavía)
1. ~~Inventario confía en el nombre que manda el navegador.~~ **Arreglado (14-nov-2026):** `_inventory_editor()` usa el usuario de la sesión (contraseña o el teclado de PIN de editor). Crear, editar, borrar, generar SKUs y aprobar solicitudes ya no leen `editor`/`approved_by` del cuerpo, y `created_by`/`updated_by`/`approved_by` se guardan con el nombre de la sesión. En el mismo cambio se quitó el `mailto` que mandaba el PIN nuevo en texto plano al correo del dueño (inventory, index, dashboard, issues_log).
2. ~~Borrados sin permiso ni auditoría.~~ **Arreglado (14-nov-2026), decisión del dueño: archivar, nunca borrar.** "Borrar" un issue, una factura o un artículo ahora pone `archived_at`, `archived_by` y `archive_reason`. El registro desaparece de las listas, queda en `_audit` (`erp.archive`) y un admin lo puede restaurar. Quién puede archivar: issues admin/boss/lead, facturas admin/boss, inventario los editores. Unir dos issues archiva el que se une (motivo "merged into …") en vez de borrarlo. Rutas nuevas, solo admin/boss: `GET /api/erp/archive/<issues|facturas|inventory>` y `POST /api/erp/archive/<tipo>/<id>/restore` (`erp.restore` en la auditoría). SQL: `migrations/erp_archive.sql`. Las listas filtran en Python, así que funcionan antes y después del SQL. Sin el SQL, archivar falla con un aviso claro y no borra nada.
   - Pendiente: falta una pantalla para ver y restaurar el archivo. Hoy solo existen las rutas de la API.
   - Pendiente (mismo problema, fuera de este arreglo): proveedores (`/api/suppliers`), unidades del proyecto (`/api/project-units`), materiales por unidad (`/api/unit-materials`) y solicitudes de material (`/api/material-requests`, solo admin) todavía se borran de verdad.
3. ~~Entregar dos veces la misma solicitud descuenta el stock dos veces.~~ **Arreglado (14-nov-2026):** la entrega primero marca la solicitud como `Delivered` solo si no lo estaba (un único cambio en la base). Si ya estaba entregada responde 409 y no toca el stock, aunque sean dos toques seguidos o dos aparatos a la vez. Si la solicitud no existe, responde 404. `delivered_by` se guarda con el nombre de la sesión.
4. ~~`/api/po-test` ruta de depuración publicada.~~ **Quitada (14-nov-2026).**
5. Filtros que pasan el texto del usuario sin escapar a Supabase (`unit`, `status`, `limit`, `item_id`). Solo lectura, riesgo bajo. Escaparlos.
- Las reglas de rol (`_ERP_ROLE_RULES`) son de Settings: si se decide que solo admin borra, se le pide a esa conversación.

## Decisiones tomadas
- Ubicaciones de trabajadores: se borran solas a los 90 días. Nada más.
