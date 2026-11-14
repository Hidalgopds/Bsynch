# Ficha: Settings (lo común de toda la plataforma)

**Esta conversación ve y maneja todo.** Es la dueña de lo que comparten las secciones, revisa lo que piden las demás y es la única que cambia las reglas de `CLAUDE.md`.

## Qué le pertenece
- Inicio de sesión y sesiones: `/login`, `/api/login`, `/api/logout`, `/api/auth/*` (2FA TOTP), `/register`, `/api/register`, `/api/forgot-password`, `/api/reset-password`, `/api/session-version`.
- Usuarios y roles del ERP y de contratistas a nivel plataforma: `/api/users*`, `/api/config/<key>` (lista blanca), `_ERP_ROLE_RULES`, `_erp_auth_guard`.
- Empresas (multi-empresa): `/platform-settings`, `/api/platform/*`, `/company-login`, `/api/company-*`, tabla `bsynch_companies`, `sb_url()`, `sb_headers()`, `_get_client_co()`.
- Seguridad: `_security_headers`, `_audit` + `audit_log`, límites (`_ip_limited`, `_key_limited`), PIN (`_pin_hash`, `_pin_match`), `_PUBLIC_FORMS`, `_retention_purge`, reporte mensual de seguridad (`/platform/security-report`, `_security_report*`, `_security_alert`), función SQL `security_self_check()`.
- Legal y páginas generales: `/privacy`, `/terms`, `templates/legal.html`, `templates/error.html`, `/robots.txt`, `/home`, `templates/home.html`.
- Infraestructura: `requirements.txt`, `Procfile`, `runtime.txt`, `migrations/`, `tests/harness.py`, `tests/test_security.py`, `tests/run_all.py`, `loadtest/`, `docs/security/`, `CLAUDE.md`, `docs/areas/`.

## Cómo está hoy
- Auth del ERP en modo `enforce` (todas las pantallas piden sesión salvo las públicas listadas en `_ERP_OPEN_EXACT`/`_ERP_OPEN_PREFIX`).
- RLS en todas las tablas sin políticas; Security Advisors sin ERROR.
- Contraseñas bcrypt; PINs con hash `h1:`; contraseña de admin de empresa al azar y con hash (se acabó el "1234").
- Bloqueos: 10 contraseñas malas por cuenta o 30 por IP en 15 min; 10 PINs malos por tablet en 10 min.
- `audit_log` con login, fallos, bloqueos, PIN, roles, soporte, configuración y empresas. No se borra nunca.
- Reporte de seguridad mensual por correo + alertas inmediatas por eventos críticos (máx. 1 por hora por tipo).
- Ubicaciones se borran a los 90 días. Nada más se borra solo.
- Páginas de privacidad y términos (Texas). `LEGAL_ENTITY` / `LEGAL_CONTACT_EMAIL` por variable de entorno.
- 127 pruebas automáticas pasando (`python tests/run_all.py`), incluida `tests/test_storage.py`.
- Fotos de órdenes de trabajo en Supabase Storage (bucket privado `job-photos`, sin políticas). Helpers comunes: `_photo_store`, `_storage_put/_get/_del`. El navegador nunca ve una URL de Storage: todo pasa por `/api/contractor/jobs/<job>/photos/<id>/img`, que revisa la empresa. Si Storage falla, la foto se guarda en la base como antes. Botón "Move photos to Storage" en `/platform/security-report` (solo dueño, queda en `audit_log`).
- Pruebas de carga k6 listas en `loadtest/`; staging creado pero **sin el esquema aplicado todavía**.

## Pendientes
- [ ] Aplicar el esquema a staging (`loadtest/export_schema.sql`) y correr k6 contra staging.
- [x] Fotos de órdenes de trabajo a Storage (`migrations/job_photos_storage.sql`, aplicada en producción principal el 2026-11-14).
- [ ] Aplicar `migrations/job_photos_storage.sql` en NNC (`fhkfpqgfzegqcyajvjlo`): el 2026-11-14 su base no respondía. Mientras tanto ahí las fotos siguen guardándose dentro de la base (respaldo automático).
- [ ] Siguientes a Storage con los mismos helpers: fotos de niños (`homelab_kid_photos`, ~1 MB), recibos (`contractor_expenses.photo_data`), archivos de contratista (`contractor_files`, hasta 7 MB c/u), fotos de órdenes de compra.
- [ ] Quitar el correo real del valor por defecto de la variable del admin de empresa en `app.py` (repo público). Antes confirmar que la variable está puesta en Render.
- [ ] `issue-photos` es un bucket **público** (heredado del ERP): pasarlo a privado y servir por la app.
- [ ] Para vender como SaaS: registro de empresa por sí misma, cobro mensual con Stripe, landing de ventas, todo en español también. Hoy `CONTRACTOR_COMPANIES` está fijo en el código (`hicons`, `bsynch`) y eso bloquea el alta de empresas nuevas.
- [ ] Pruebas para ERP, Home Lab y Marketing a medida que se trabajen (cada sección agrega su archivo).

## Pendientes del dueño (fuera del código; recordarle)
- Pasar el repositorio de GitHub a **privado**.
- Regenerar el secreto de QuickBooks (se vio en una captura).
- Supabase Pro con respaldos diarios y luego poner `BACKUPS_CONFIRMED=1` en Render.
- Confirmar en Render que `ERP_AUTH_MODE` no está en `report`.
- Verificación en dos pasos en Render, Supabase, GitHub, Google, Namecheap, Anthropic, Resend.
- Variables en Render: `SECURITY_REPORT_TO`, `LEGAL_ENTITY`, y `KIOSK_ADMIN_PASS` si usan la tablet.
- Servicio de staging en Render; Gmail emisor de Hicons; cuenta de Stripe y precios.

## Decisiones tomadas
- Fotos: bucket privado y la app las sirve (no URLs firmadas ni públicas), así la regla "cada empresa ve solo lo suyo" vive en un solo lugar. Borrar una foto (acción manual) borra también su archivo.
- Un solo worker de gunicorn: los límites de intentos viven en memoria (si se suben workers, moverlos a la base).
- Reporte de seguridad: mensual (día 1) + alertas inmediatas; va al dueño (`DEFAULT_COMPANY_ADMIN_USER` o `SECURITY_REPORT_TO`).
- Acceso de soporte del admin a una empresa: solo si su Manager lo da (24 o 72 h) y todo queda registrado.
