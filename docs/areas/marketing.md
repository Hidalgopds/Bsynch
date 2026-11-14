# Ficha: Marketing

Campañas, leads y herramientas de crecimiento. **Hoy está vacía**: `/marketing-hub` solo muestra "Under construction — coming soon".

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

## Decisiones
- La landing sigue con `noindex` (cabecera general de Settings) hasta que haya precios. Para que Google la indexe, Settings tiene que permitir `index` solo en `/marketing`.
- Sin chino por ahora: el dueño pidió inglés y español.

## Pendientes
- [ ] Precios reales (decisión del dueño).
- [ ] Formulario de leads (`marketing_leads`, honeypot + límite por IP) en lugar del botón de correo.
- [ ] Botón "Empezar" hacia el registro de empresas cuando Settings lo tenga.
- [ ] Decidir si `bsynch.com/` (hoy manda a `/login`) debe mostrar la landing. Eso toca la ruta `/`, hay que coordinarlo con Settings.
