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

## Pendientes
- [ ] Empresas fijas en el código (`CONTRACTOR_COMPANIES`): para vender a más contratistas hace falta que se den de alta solas (coordinar con Settings).
- [x] Fotos de órdenes de trabajo a Storage (hecho por Settings, 2026-11-14). Mismas rutas y pantallas; las plantillas no cambiaron.
- [ ] Recibos de gastos (`contractor_expenses.photo_data`) y `contractor_files` a Storage: los hace Settings con los mismos helpers.
- [ ] Renee creó 5 órdenes duplicadas el día del error de `uploadWoMaterials`; las borra ella desde la app.
- [ ] Gmail emisor para Hicons (lo configura el dueño).

## Decisiones tomadas
- Nada de facturas, órdenes, fotos o recibos se borra solo. Borrar es siempre una acción manual del usuario con permiso.
- Colores con contraste AA (teal `#0f766e`).
