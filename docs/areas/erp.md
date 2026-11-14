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

## Pendientes
- [ ] Escribir `tests/test_erp.py` con los flujos principales (inventario, issues, compras, timesheet).
- [ ] Revisar con el dueño qué pantallas siguen en uso y cuáles se pueden retirar.

## Decisiones tomadas
- Ubicaciones de trabajadores: se borran solas a los 90 días. Nada más.
