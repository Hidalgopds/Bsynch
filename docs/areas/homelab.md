# Ficha: Home Lab (Family Hub)

La parte familiar: checklist de los niños, juegos y Hermaniland. Guarda datos de **menores**, así que va con más cuidado que el resto.

## Qué le pertenece
- Páginas: `/homelab-hub`, `/homelab/kids-checklist`, `/homelab/legal`, `/homelab/games-hub`, `/homelab/games*`, `/games`, `/homelab/tball`, `/hermaniland`.
- API: `/api/homelab/*`, `/api/stop/*` (juego Stop, público a propósito), `/api/hermaniland/*`.
- Plantillas: `homelab-*.html`, `hermaniland.html`.
- Datos de Hermaniland: `hermaniland_*.py`, `hermaniland_players_*.csv/json/txt`, `regenerate_players_fixed.py`.
- Tablas: `homelab_kids`, `homelab_guardians`, `homelab_kid_photos` y las de Hermaniland.
- Pruebas: `tests/test_homelab.py` (las de seguridad de Home Lab están en `test_security.py`, que es de Settings).

## Cómo está hoy
- La API de Home Lab pide sesión; las páginas mandan al login si no hay sesión (`_hl_page_guard`, `_hl_family_session`).
- PIN de padre/tutor con hash, no se devuelve nunca, y se bloquea tras 10 intentos malos.
- Solo un padre o tutor registra a un niño (acepta el aviso de `/homelab/legal`).
- El juego Stop sigue público (salas de juego, sin datos personales).
- `tests/test_homelab.py` (116 pruebas): páginas, tutores y PIN, niños, fotos (máx. 5), bloques y tareas, checklist (marcar, desmarcar con PIN, aprobación del padre), ruleta de juegos por edad, ajustes, aislamiento entre familias (subdominio), límite del plan gratis, Stop completo y Hermaniland de principio a fin contra la IA.

## Hecho
- 2026-11-14: pruebas de Home Lab. Arreglos que salieron de ellas:
  - Stop: la sala de espera fallaba siempre (pedía un dato `duration` que no existe), así que los invitados nunca veían empezar la partida. Ahora responde y les da el tiempo y las categorías del anfitrión.
  - Hermaniland: si la IA hacía la última elección del draft, la partida se quedaba trabada y nunca pasaba a la revisión. Ahora pasa sola. La IA ya no elige más de 11.
  - Hermaniland: elegir formación con un jugador que no está en la sala daba error 500; ahora da 404.

## Pendientes
- [ ] **Importante (datos de menores)**: en `bsynch.com` cualquier persona con sesión (un trabajador de Hicons, un líder de Bsynch, alguien sin empresa, una cuadrilla con PIN) puede ver y editar los niños y sus fotos de la familia principal. Falta decidir quién es "la familia" en el dominio principal (por ejemplo, solo el dueño o una lista de usuarios). El permiso vive en `_erp_access_denied` y los roles, que son de Settings: pedirlo allá.
- [ ] Stop: cualquiera que sepa el código de sala puede iniciar la partida (no se revisa que sea el anfitrión).
- [ ] Stop: los nombres de jugadores se pintan como HTML en la página (`homelab-stop.html`): un nombre con código podría ejecutarse en el navegador de los otros jugadores. Pasarlo a texto.
- [ ] Ordenar los archivos sueltos de Hermaniland (varias versiones de la lista de jugadores) cuando el dueño diga cuál es la buena.

## Reglas propias
- Nunca exponer fotos ni nombres de niños en enlaces públicos.
- Nada de datos de niños en pruebas: nombres inventados.
