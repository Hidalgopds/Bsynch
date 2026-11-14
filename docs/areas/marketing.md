# Ficha: Marketing

Campañas, leads y herramientas de crecimiento. Hoy tiene: landing pública `/marketing` (EN/ES) con formulario de leads, y la lista de leads en `/marketing-hub` (solo dueño de plataforma). Campañas: pendiente.

## Qué le pertenece
- Página: `/marketing-hub` (`templates/marketing-hub.html`).
- Todo lo nuevo de marketing: usar rutas `/marketing/*` y `/api/marketing/*`, plantillas `marketing-*.html`, tablas `marketing_*`.
- Pruebas: `tests/test_marketing.py` cuando haya funciones.

## Ideas ya conversadas (por decidir con el dueño)
- Landing de ventas de BSynch para contratistas (en inglés y español) con precios y registro.
- Captura de leads desde la landing hacia una lista simple.

## Coordinación
- El registro de empresas nuevas y el cobro mensual (Stripe) son de **Settings**; Marketing hace la página que vende y manda a ese registro.
- Formularios públicos: usar el honeypot y el límite por IP que ya existen (`_PUBLIC_FORMS`).

## Hecho
- **2026-11-14: Landing pública de ventas** en `/marketing` (`templates/marketing-landing.html`), inglés y español.
  - Idioma: `?lang=en|es`; si no viene, el idioma del navegador; si no, inglés. Selector EN/ES arriba.
  - Secciones: portada, 6 funciones, cómo funciona (3 pasos), seguridad, precios, llamada final.
  - Botones "Request a demo" abren correo a `LEGAL_CONTACT` (correo del negocio, variable de Render). "Sign in" va a `/login`.
  - Solo promete lo que la app ya hace. No hay precios inventados ni promesa de respaldos.
  - `/marketing-hub` tiene un botón para ver la landing.
  - Prueba: `tests/test_marketing.py`.
- **2026-11-14: Formulario de leads.**
  - Tabla `marketing_leads` (`migrations/marketing_leads.sql`), solo en el proyecto principal. RLS activo, sin políticas.
  - Envío público: `POST /api/public/marketing/lead`. Va bajo `/api/public/` porque ese prefijo ya está abierto en la guardia del ERP, así no se tocó la guardia. Honeypot `website` + 10 envíos por IP por hora (una línea agregada a `_PUBLIC_FORMS`).
  - Pide nombre y al menos correo o teléfono. Errores en el idioma del visitante. Solo en `bsynch.com`; en subdominios de clientes responde 404.
  - Cada lead nuevo: `_audit("marketing.lead_created")` y correo al dueño (`DEFAULT_COMPANY_ADMIN_USER`) con reply-to al lead.
  - Lista: `GET /api/marketing/leads` (filtro `?status=`), `PATCH /api/marketing/leads/<id>` para estado (new, contacted, won, lost) y notas. Solo `_is_platform_operator()`. Cambios auditados. **No hay ruta para borrar.**
  - Si la base falla, el visitante ve el correo de contacto para no perder el lead.

## Decisiones
- La landing sigue con `noindex` (cabecera general de Settings) hasta que haya precios. Para que Google la indexe, Settings tiene que permitir `index` solo en `/marketing`.
- Sin chino por ahora: el dueño pidió inglés y español.

## Pendientes
- [ ] Precios reales (decisión del dueño).
- [x] `migrations/marketing_leads.sql` aplicada en producción (`wanfpiogchwttsippekm`) el 2026-11-14. RLS activo, 0 políticas, 0 filas. Security Advisors: cero ERROR. Solo el INFO "RLS sin políticas" de siempre (58 tablas, antes 57). No se aplica en NNC.
- [ ] Aviso a Settings: se agregó una línea a `_PUBLIC_FORMS` (`f-lead`, 10/hora).
- [ ] Botón "Empezar" hacia el registro de empresas cuando Settings lo tenga.
- [ ] Decidir si `bsynch.com/` (hoy manda a `/login`) debe mostrar la landing. Eso toca la ruta `/`, hay que coordinarlo con Settings.
