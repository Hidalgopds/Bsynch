# Ficha: Settings (lo común de toda la plataforma)

**Esta conversación es la de BSynch como plataforma** (lo que se vende como SaaS) y además de la pantalla Settings. **Ve y maneja todo.** Es la dueña de lo que comparten las secciones, revisa lo que piden las demás y es la única que cambia las reglas de `CLAUDE.md`.

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
- [ ] Si NNC se reactiva: aplicarle `migrations/job_photos_storage.sql`. Mientras tanto ahí las fotos siguen guardándose dentro de la base (respaldo automático).
- [ ] Siguientes a Storage con los mismos helpers: fotos de niños (`homelab_kid_photos`, ~1 MB), recibos (`contractor_expenses.photo_data`), archivos de contratista (`contractor_files`, hasta 7 MB c/u), fotos de órdenes de compra.
- [ ] Quitar el correo real del valor por defecto de la variable del admin de empresa en `app.py` (repo público). Antes confirmar que la variable está puesta en Render.
- [ ] `issue-photos` es un bucket **público** (heredado del ERP): pasarlo a privado y servir por la app.
- [x] Empresas de Contractor en la tabla `contractor_companies` (2026-11-14). `CONTRACTOR_COMPANIES` es un registro que se lee de la tabla cada minuto; hicons y bsynch siempre están; si la tabla falla queda la última lista buena. Alta por `POST /api/platform/contractor-companies` (solo dueño, en `audit_log`). Pruebas: `tests/test_companies.py`.
- [x] Pantalla para dar de alta empresas: "Add a company" en Platform Admin (`/contractor/platform`), 2026-11-14. Arma el id corto solo desde el nombre. Ids bloqueados: `_RESERVED_SLUGS` en `app.py` (igual que `NOT_CO` en `static/contractor-scope.js`; si se agrega una pantalla `/contractor/<x>`, sumarla en las dos listas).
- [x] Registro + cobro (2026-11-14). Decisiones del dueño: plan fijo + por persona (por ahora $49/mes incluye 5, $8 por persona extra: `SAAS_BASE_USD`, `SAAS_INCLUDED_SEATS`, `SAAS_SEAT_USD`), 14 días gratis sin tarjeta, **el dueño aprueba cada empresa**, se vende Contractor (ERP cuando separe empresas).
  - `/signup` (es/en) → empresa `pending` en `contractor_companies` + cuenta sin aprobar (Manager). Anti-spam: honeypot + 5 por hora por conexión.
  - Platform Admin → "Waiting for your approval": Approve (prueba de 14 días, correo al cliente) / Reject (queda guardada, nunca se borra).
  - `/billing?company=` (es/en), botón 💳 Billing en la barra de Contractor solo para el Manager de empresas que pagan. Stripe Checkout + portal de Stripe. Webhook `/api/stripe/webhook` con firma. Cada día se ajusta la cantidad de personas extra en Stripe.
  - Sin pago al terminar la prueba: **puede leer y exportar todo, no editar** (402 + aviso). Hicons y Bsynch exentas (`billing_exempt`). Sin Stripe configurado no se bloquea a nadie.
  - **Usuarios de empresas cliente solo entran a Contractor y Billing** (`_saas_scope_guard`): ERP, Home Lab, Marketing y Settings bloqueados en el servidor; `/home` muestra solo Contractor.
  - Pruebas: `tests/test_billing.py`. SQL: `migrations/saas_billing.sql` (aplicado).
- [x] **Arreglado (2026-11-14): `/api/forgot-password` era un hueco grave.** Cambiaba la clave de cualquier cuenta sabiendo su correo y, sin Gmail configurado, devolvía la clave nueva en la respuesta. Ahora manda un enlace de un solo uso. Revisar en `audit_log` y con el dueño si alguien la usó antes (no quedaba registrado).
- [x] "Add a company" pide (opcional) nombre y correo del Manager: se crea su cuenta sin clave conocida y le llega el enlace para elegirla. La empresa arranca con su prueba gratis. Pruebas: `tests/test_passwords.py`.
- [ ] El dueño debe entrar con `daniel@hidalgoops.com` (no con "Daniel Hidalgo", que es de Hicons) y activarle 2FA.
- [ ] `/api/reset-password` (admin cambia la clave de otro, mínimo 4 caracteres) sigue existiendo para la pantalla vieja de ERP: pasarlo a "mandar enlace" y subir el mínimo.
- [ ] **Dueño:** crear cuenta Stripe, 2 precios mensuales (base y por persona), webhook a `https://bsynch.com/api/stripe/webhook` (eventos `checkout.session.completed`, `customer.subscription.*`, `invoice.payment_failed`) y activar el portal de clientes. Variables en Render: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_BASE`, `STRIPE_PRICE_SEAT` (y `SAAS_*` si cambian los precios mostrados).
- [ ] ERP: agregar columna de empresa a sus tablas para poder venderlo (lo hace la conversación de ERP). Hasta entonces `SAAS_HUBS_READY = {"contractor"}`.
- [ ] Landing de ventas (Marketing) que lleve a `/signup`. `robots.txt` hoy bloquea todo: abrir `/signup` y la landing cuando se lance.
- [ ] `ADMIN_EMAIL` y `DEFAULT_COMPANY_ADMIN_USER` tienen el correo real como valor por defecto en `app.py`: sacarlo cuando el dueño confirme las variables en Render.
- [ ] Subdominios por empresa: confirmar DNS + dominio en Render y que la sesión sirve entre subdominios (lo pide Contractor antes de prender "dirección propia").
- [ ] Cobro mensual con Stripe, landing de ventas, todo en español también.
- [ ] NNC: pausado, el trabajo con esa empresa se paró. No aplicarle migraciones mientras siga pausado.
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
- **Dueño de la plataforma = cuenta `Daniel Admin`** (usuario de `DEFAULT_COMPANY_ADMIN_USER`, sin empresa). El dueño **ve los datos de todas las empresas sin pedir acceso de soporte** (decisión del dueño, 2026-11-14); cada visita queda en el `contractor_support_log` de esa empresa, que su Manager ve, y la política de privacidad lo dice. Los demás admins de plataforma siguen necesitando acceso de soporte. Ojo: un cliente grande o una auditoría SOC 2 puede pedir quitarlo.
- **Contraseñas: nunca una clave inventada por otro, mandada por correo o mostrada.** Cuenta nueva o "olvidé mi contraseña" = enlace de un solo uso (`password_links`, solo se guarda el hash): 72 h para cuenta nueva, 1 h para cambio. Pedir un enlace nuevo anula el anterior. "Forgot password" responde igual exista o no el correo.
- Fotos: bucket privado y la app las sirve (no URLs firmadas ni públicas), así la regla "cada empresa ve solo lo suyo" vive en un solo lugar. Borrar una foto (acción manual) borra también su archivo.
- Un solo worker de gunicorn: los límites de intentos viven en memoria (si se suben workers, moverlos a la base).
- Reporte de seguridad: mensual (día 1) + alertas inmediatas; va al dueño (`DEFAULT_COMPANY_ADMIN_USER` o `SECURITY_REPORT_TO`).
- Acceso de soporte del admin a una empresa: solo si su Manager lo da (24 o 72 h) y todo queda registrado.
