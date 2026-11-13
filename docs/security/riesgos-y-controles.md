# Riesgos y estado de los controles

**Actualizado:** 13 de noviembre de 2026

## Controles implementados
| Control | Dónde |
|---|---|
| Toda ruta del ERP exige sesión (`ERP_AUTH_MODE` es `enforce` por defecto) | `app.py` → `_erp_auth_guard` |
| Permisos por rol en el servidor (trabajadores, PIN, configuración, notificaciones) | `_ERP_ROLE_RULES` |
| Cada persona solo cambia su propia cuenta (o la cambia un admin) | `_ERP_SELF_ROUTES` |
| Aislamiento entre empresas y acceso de soporte con permiso del Manager y registro | módulo de contratistas |
| RLS en todas las tablas; la clave pública no lee nada | Supabase |
| Contraseñas con bcrypt; PINs (ERP, kiosko, Home Lab) con HMAC; admin de empresas con bcrypt | `_pin_hash`, `hash_password` |
| Límites de intentos: login, PIN, kiosko, tablet, login de empresas, Home Lab | `_ip_limited`, `_key_limited` |
| Verificación en dos pasos (TOTP), obligatoria por empresa | `/api/auth/2fa` |
| Registro de auditoría permanente | tabla `audit_log` |
| Encabezados de seguridad (HSTS, anti-clickjacking, nosniff, permisos de cámara y ubicación) | `_security_headers` |
| Ubicación borrada a los 90 días (lo único que se borra solo) | `_retention_purge` |
| Las claves de las empresas cliente nunca van al navegador | `/api/platform/companies` |
| Home Lab (datos de menores) requiere sesión | `_hl_page_guard` |
| Copia de cada factura y estimado enviado a un buzón de archivo (opcional) | Settings → Invoices |
| Política de privacidad y términos publicados | `/privacy`, `/terms` |

## Pendientes (dueño de la plataforma)
| # | Acción | Por qué | Prioridad |
|---|---|---|---|
| 1 | Poner el repositorio de GitHub en **privado** | Hoy cualquiera puede leer el código y su historial | Alta |
| 2 | Regenerar el client secret de QuickBooks | Salió en una captura de pantalla | Alta |
| 3 | Activar respaldos: Supabase Pro | Hoy no hay ninguna copia de la base de datos | Alta |
| 4 | Confirmar que en Render **no** está `ERP_AUTH_MODE=report` | Volvería a abrir el ERP | Alta |
| 5 | 2FA en Render, Supabase, GitHub, Google, Namecheap, Anthropic y Resend | Son las llaves de todo | Alta |
| 6 | Revisar los documentos legales con un abogado y poner `LEGAL_ENTITY` en Render | Hoy dicen "BSynch" como empresa | Media |
| 7 | Completar los contactos en `respuesta-incidentes.md` | Para tenerlos a mano | Media |

## Riesgos aceptados (con motivo)
| Riesgo | Por qué se acepta | Revisar si… |
|---|---|---|
| La carpeta `issue-photos` (fotos viejas del ERP) es pública por enlace | Los nombres son aleatorios e imposibles de adivinar y la carpeta no se puede listar; pasarla a privada rompería enlaces guardados | Se vuelve a usar el módulo de issues con datos sensibles |
| Los PINs son de 4 dígitos | Es lo práctico en obra; lo compensan los límites de intentos y el cifrado | Se usa el PIN para algo más que marcar o abrir el ERP |
| Los límites de intentos viven en memoria (se reinician al desplegar) | Un solo proceso en Render; suficiente para frenar ataques automáticos | Se escala a varios procesos o servidores |
| La sesión dura 30 días | Trabajadores en el teléfono en obra; se puede cerrar por usuario y globalmente | Un cliente exige sesiones más cortas |
| La IA lee fotos de recibos | Solo la imagen y por pedido del usuario; está declarado en `/privacy` | Cambian los términos del proveedor |
