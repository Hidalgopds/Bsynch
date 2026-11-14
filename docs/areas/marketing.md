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

## Pendientes
- [ ] Definir con el dueño qué es lo primero que quiere ver aquí.
