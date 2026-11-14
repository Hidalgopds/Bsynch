# Hermaniland: archivo

Versiones viejas de los datos del juego. **Nada de esto lo carga la app**: se guardan por si sirven de referencia más adelante. El juego usa solo los archivos de la carpeta de arriba (`hermaniland/`).

| Archivo | Qué es |
|---|---|
| `hermaniland_players_7500.csv` / `.json` / `.txt` | Lista grande de 7500 jugadores (la misma en 3 formatos). Era la entrada de `regenerate_players_fixed.py`. |
| `hermaniland_players_7500_FINAL.csv` | Otra versión de la lista de 7500, con datos distintos. |
| `hermaniland_players_366_PREMIUM.csv` / `.json` | Lista "premium" de 366 jugadores. |
| `hermaniland_players_COMPLETE.csv`, `_HISTORIC.csv`, `_NUEVA_BASE.csv` | Otras listas de prueba. |
| `hermaniland_data_complete.py`, `hermaniland_data_new.py` | Versiones anteriores de la base de datos del juego. |
| `hermaniland_coaches_legends.py` | Entrenadores "leyenda" que nunca se conectaron al juego. |
| `regenerate_players_fixed.py` | Script viejo que generaba las listas por posición desde el CSV de 7500. Tiene rutas fijas de otra máquina: no correrlo sin revisarlo. |

Movidos aquí el 2026-11-14. Para recuperar uno, basta con moverlo de vuelta y conectarlo en `hermaniland/players.py` o en `app.py`.
