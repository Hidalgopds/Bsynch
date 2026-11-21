# Ficha: Contractor (contratistas)

App para empresas contratistas (hoy **Hicons** y **Bsynch**). Se instala en el teléfono (PWA) y abre directo en **Projects** (`/contractor/projects?company=<empresa>`).

## Qué le pertenece
- Páginas: `/contractor-hub`, `/contractor/*` (projects, workorders, calendar, contacts, estimates, invoicing, expenses, dashboard, mailroom, company settings, account, agreement, platform), `/join/<token>`, `/i/<token>` (factura pública), `/e/<token>` (estimado público).
- API: `/api/contractor/*`, `/api/join/*`, `/api/public/invoice/*`, `/api/public/estimate/*`.
- Plantillas `templates/contractor-*.html`; `static/ct-*.js`, `static/contractor-light.css`.
- Tablas: `contractor_jobs`, `contractor_projects`, `job_steps`, `job_photos`, `job_visits`, `job_materials`, `job_receipts`, `contractor_contacts`, `contractor_client_folders`, `contractor_estimates`, `contractor_invoices`, `contractor_expenses`, `contractor_mail_log`, `contractor_support_log`, `contractor_locations`, `contractor_agreements`.
- Pruebas: `tests/test_contractor.py`.

## Roles
- **Manager** (`admin`): todo en su empresa, invita gente, cambia roles, factura, da acceso de soporte.
- **Leader** (`lead`): maneja órdenes y cuadrilla.
- **User** (`member`): ve y trabaja lo suyo; lo que crea avisa al Manager.
- Cada empresa ve solo lo suyo. El admin de plataforma entra solo con acceso de soporte (24/72 h, registrado).

## Cómo está hoy
- Proyectos → órdenes de trabajo (con visitas, fotos con notas, materiales, recibos con lectura por IA, progreso por % / checklist).
- **Maestro de clientes en carpetas**: el Manager crea carpetas con nombre y color, mete clientes; clientes nuevos con el mismo dominio de correo caen solos en la carpeta (no adivina con gmail/hotmail…).
- Estimados y facturas con numeración por prefijo y rango, PDF, envío por correo, enlace público, recordatorios, estados (Not sent / Sent / In process / Paid).
- Factura solo si la orden está terminada (100%) y tiene precio.
- **Copia de archivo**: si la empresa pone un correo de archivo, cada factura/estimado enviado manda una copia ahí (el cliente no la ve).
- Vista previa del enlace al compartir (número, empresa, logo; sin montos ni dirección).
- Correos: por empresa (`_ct_mail`), quedan en `contractor_mail_log`.
- El dictado de órdenes por voz **se quitó** a pedido del dueño.
- **Impuesto, descuento y vencimiento** (aprobado por Renee): la empresa pone su sales tax (%) y "Clients pay within" (Net 7/15/30/45/60) en Company settings. Facturas y estimados nuevos llevan Subtotal, Discount ($), Sales tax y Total (`_ct_totals`); se pueden cambiar en cada uno. Estimado → orden de trabajo guarda el precio antes de impuesto, y la factura vuelve a aplicar el descuento y el impuesto que el cliente aceptó. Cada factura nueva tiene `due_date`. Atrasada (`_ct_inv_overdue`): pasó su fecha de vencimiento; si es "Due on receipt", cuando lleva los días de recordatorio sin pagarse desde que se mandó. La misma regla usan la lista, el dashboard y el correo diario. SQL: `migrations/contractor_tax_due.sql`.
- **Carpetas en Work orders** (pantalla de inicio del teléfono, `contractor-projects.html`): "In progress", "Completed" y una carpeta por cliente (su Client folder si tiene, si no su nombre; adentro se separa In progress / Completed). Los proyectos reales siguen abajo. Al llegar al 100% la app pregunta si se mueve a Completed (`POST /api/contractor/jobs/<id>/archive`, columna `archived_at`). Se reactiva desde Completed; si baja de 100% o se reabre, sale sola. No se borra nada; queda en el historial de visitas. Los KPIs de arriba cuentan solo lo que no está en Completed. SQL: `migrations/contractor_jobs_archive.sql` (aplicado).
- **Factura ya enviada**: el botón cambia a "✓ Sent · Send again" (verde). Reenviar pide confirmación y el servidor lo exige (`resend: true`, si no 409), así no sale doble por error. El historial dice "Sent again to…".
- **Dirección web propia** (`<empresa>.bsynch.com`): el Manager la prende en Company settings → Security. Desde ahí, enlaces de facturas, estimados, invitaciones y correos de alerta usan esa dirección (`_ct_web_base`). Apagada por defecto. Se niega a prenderse si ese subdominio está conectado a otra base de datos en `bsynch_companies` (los enlaces saldrían rotos). Queda en `audit_log` (`contractor.web_address`). En la dirección propia, el admin de plataforma cae directo en esa empresa.

## Pendientes
- [ ] **"Agregar persona" en Admin settings (pedido de Settings, 2026-11-21).** El Manager escribe nombre, correo y rol; se crea la cuenta en su empresa, sin clave conocida, y a la persona le llega un enlace de un solo uso (72 h) para elegir la clave. Usar los helpers de Settings: `_pw_link_new(nombre, "setup", by=...)` y `_pw_link_email(...)`. Revisar que el nombre, usuario y correo no existan; rol en `contractor_roles_<empresa>`; `_audit("company.member_invited", ...)`. Solo el Manager de esa empresa (`_ct_is_own_manager`) o el dueño. Empresas demo: no mandar correo a `@example.com`. Prueba: una empresa no puede agregar gente a otra. El enlace de invitación (`/join`) se queda para invitar a varios a la vez.
- [ ] **Más adelante (lo coordina Settings, ver su ficha):** botón "Pagar en línea" en la factura pública con Stripe Connect; BSynch cobra una comisión por pago. No empezar hasta que Settings active Stripe y Connect.
- [x] Empresas ya no fijas en el código: `CONTRACTOR_COMPANIES` se lee de la tabla `contractor_companies` (hecho por Settings, 2026-11-14). El hub arma una tarjeta por empresa solo. No vuelvas a escribir `hicons`/`bsynch` a mano en pantallas nuevas. `static/contractor-scope.js` ya reconoce cualquier empresa en `/contractor/<empresa>/...`; si creas una pantalla nueva `/contractor/<x>`, agrega `<x>` a `NOT_CO` ahí y a `_RESERVED_SLUGS` en `app.py` (lo hace Settings). Alta de empresas: "Add a company" en Platform Admin. (2026-11-21) La tarjeta Platform Admin del hub ahora va a `/platform?hub=contractor` (página única de Settings); `/contractor/platform` sigue siendo la lista de gente.
- [x] Fotos de órdenes de trabajo a Storage (hecho por Settings, 2026-11-14). Mismas rutas y pantallas; las plantillas no cambiaron.
- [x] Recibos de gastos a Storage (Settings, 2026-11-21): se mueven solos (`contractor_expenses.photo_path`, bucket `job-photos`, carpeta `receipts-<empresa>`). Los visores reciben un enlace de la app (`/api/contractor/jobs/<job>/receipts/<id>/img` o `/api/contractor/<empresa>/expenses/<id>/img`). `contractor_files` sigue vacía; cuando se use, mismo camino.
- [ ] Pagos parciales y anticipos (punto 3 aprobado para después).
- [ ] Renee creó 5 órdenes duplicadas el día del error de `uploadWoMaterials`; las borra ella desde la app.
- [ ] Gmail emisor para Hicons (lo configura el dueño).

- [ ] Dirección propia: Settings debe confirmar que cada subdominio (ej. `hicons.bsynch.com`) responden (DNS + dominio en Render) y que la sesión sirve entre subdominios. Hasta entonces, no prenderla en producción.

## Decisiones tomadas
- Nada de facturas, órdenes, fotos o recibos se borra solo. Borrar es siempre una acción manual del usuario con permiso.
- Colores con contraste AA (teal `#0f766e`).
- El enlace de acceso (`/login`) en el correo de cuenta aprobada sigue en el host actual: el login es de Settings.
- Textos de ayuda y placeholders sin nombres de empresas reales (las ven todas las empresas nuevas).
