# Ficha: Home Lab (Family Hub)

La parte familiar: checklist de los niños, juegos y Hermaniland. Guarda datos de **menores**, así que va con más cuidado que el resto.

## Qué le pertenece
- Páginas: `/homelab-hub`, `/homelab/kids-checklist`, `/homelab/legal`, `/homelab/games-hub`, `/homelab/games*`, `/games`, `/homelab/tball`, `/hermaniland`.
- API: `/api/homelab/*`, `/api/stop/*` (juego Stop, público a propósito), `/api/hermaniland/*`.
- Plantillas: `homelab-*.html`, `hermaniland.html`.
- Datos de Hermaniland: `hermaniland_*.py`, `hermaniland_players_*.csv/json/txt`, `regenerate_players_fixed.py`.
- Tablas: `homelab_kids`, `homelab_guardians`, `homelab_kid_photos` y las de Hermaniland.
- Pruebas: crear `tests/test_homelab.py` (las de seguridad de Home Lab están en `test_security.py`, que es de Settings).

## Cómo está hoy
- La API de Home Lab pide sesión; las páginas mandan al login si no hay sesión (`_hl_page_guard`, `_hl_family_session`).
- PIN de padre/tutor con hash, no se devuelve nunca, y se bloquea tras 10 intentos malos.
- Solo un padre o tutor registra a un niño (acepta el aviso de `/homelab/legal`).
- El juego Stop sigue público (salas de juego, sin datos personales).

## Pendientes
- [ ] Escribir `tests/test_homelab.py` (checklist, juegos, Hermaniland).
- [ ] Ordenar los archivos sueltos de Hermaniland (varias versiones de la lista de jugadores) cuando el dueño diga cuál es la buena.

## Reglas propias
- Nunca exponer fotos ni nombres de niños en enlaces públicos.
- Nada de datos de niños en pruebas: nombres inventados.
