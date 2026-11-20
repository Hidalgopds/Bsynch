# Ficha: Storefront

Catálogo en línea siempre al día para **tiendas locales** (electrodomésticos, muebles, colchones, open box, usados) que hoy no tienen página web porque cargar productos toma tiempo y la mercancía rota rápido. La promesa: **sin escribir**. Foto, precio, publicado. En español la llamamos "Local Comercial"; en la app se llama **Storefront**.

Estado (2026-11-20): **en construcción, sin pantallas todavía.** El hub `/storefront-hub` y su tarjeta en `/home` solo los ven los admins de plataforma. Esqueleto hecho por Settings.

## Antes de construir: validar (pendiente del dueño)
- [ ] Visitar 5 tiendas y preguntar: cómo venden hoy (Facebook, Marketplace, WhatsApp, Instagram), quién sube las fotos, cuánto tiempo les toma y si pagarían (ej. $29/mes) por un catálogo que se arma solo.
- [ ] Si 2 o 3 dicen "sí, ¿cuándo?", se construye la primera versión. Si no, se deja quieto.
- El competidor real es **Facebook/WhatsApp** (gratis y conocidos), no otras apps. No competir con Facebook: alimentarlo más rápido.

## Qué le pertenece
- Página: `/storefront-hub` (`templates/storefront-hub.html`). Ruta y guardia en `app.py` (`storefront_hub`): hoy solo admins de plataforma.
- Todo lo nuevo: rutas `/storefront/*` y `/api/storefront/*`, catálogo público en `/s/<tienda>` (o `<tienda>.bsynch.com` cuando estén los subdominios), plantillas `storefront-*.html`, tablas `storefront_*`, pruebas `tests/test_storefront.py`.
- Nombres reservados para que ninguna empresa los use como id: `storefront`, `store`, `stores`, `shop`, `catalog`, `tienda` (en `_RESERVED_SLUGS`).

## Primera versión (lo que se acordó con el dueño)
1. **Foto y listo:** foto del producto y de su etiqueta; la IA (Claude con visión, como los recibos de Contractor) llena marca, modelo, medida y especificaciones. La persona solo revisa.
2. **Precio y cantidad**, publicar.
3. **Vendido / Apartado** con un toque. Lo vendido sale solo del catálogo.
4. **Catálogo público por tienda**, pensado para teléfono, con botón **"Preguntar por WhatsApp"** en cada producto (abre WhatsApp con el producto escrito).
5. **Compartir** un producto a Facebook, Marketplace o estados de WhatsApp con un toque.
6. Inglés y español; apartados / layaway.

## Reglas propias (además de CLAUDE.md)
- **Toda tabla `storefront_*` lleva `company` desde el primer día** y cada consulta filtra por la empresa de quien llama (modelo de base compartida). Prueba obligatoria: una tienda no ve ni edita lo de otra.
- **Fotos a Supabase Storage** con los helpers de Settings (`_photo_store`, `_storage_get`), nunca dentro de la base. Para el catálogo público se servirán por una ruta de la app que solo entrega fotos de productos **publicados**.
- El catálogo público no muestra datos internos (costo, proveedor, notas, quién lo subió).
- Precios y textos que salen al público se escapan siempre (nada de HTML del usuario).
- Formularios públicos (si los hay): honeypot + límite por IP (`_PUBLIC_FORMS`, lo agrega Settings).
- Empresas, registro, aprobación, cobro y acceso de usuarios son de **Settings**. Para vender Storefront, Settings lo agrega a `SAAS_HUBS` / `SAAS_HUBS_READY` y a la página de registro (que hoy es de contratistas: necesitará su propia versión).

## Pendientes
- [ ] Validación con tiendas (arriba).
- [ ] Diseño de tablas: `storefront_products` (company, título, marca, modelo, categoría, especificaciones jsonb, precio, cantidad, estado: borrador/publicado/apartado/vendido, fotos, creado_por, fechas) y `storefront_settings` por tienda (nombre público, WhatsApp, dirección, horario, logo).
- [ ] Settings: abrir el hub a empresas cliente cuando haya primera versión (hoy `_saas_scope_guard` los manda a Contractor).

## Decisiones tomadas
- Nombre en la app: **Storefront** (dueño, 2026-11-20).
- Va después de activar Stripe y de los primeros clientes de Contractor; no compite por tiempo con eso.
