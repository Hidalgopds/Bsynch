# Política de seguridad de la información

**Versión:** 1.0 · **Fecha:** 13 de noviembre de 2026 · **Dueño:** responsable de la plataforma BSynch (Daniel Hidalgo) · **Revisión:** anual

## 1. Objetivo y alcance
Proteger la confidencialidad, integridad y disponibilidad de la información de BSynch y de las empresas que la usan (clientes como Hicons), incluidos los datos personales de sus trabajadores, sus clientes y, en Home Lab, de menores.

Aplica a: la aplicación (código, servidor en Render, base de datos en Supabase), las cuentas de administración de esos servicios, los equipos desde donde se administran y cualquier persona con acceso.

## 2. Responsabilidades
| Rol | Responsabilidad |
|---|---|
| Dueño de la plataforma | Aprueba esta política, administra los servicios (Render, Supabase, GitHub, correo), revisa accesos y avisos de seguridad, responde a incidentes |
| Manager de cada empresa cliente | Decide quién entra a su empresa, con qué rol, y si da acceso de soporte |
| Usuarios | Cuidan su contraseña, PIN y códigos; avisan si ven algo raro |

## 3. Clasificación de la información
| Nivel | Ejemplos | Regla |
|---|---|---|
| **Secreta** | Claves de Supabase, `SECRET_KEY`, claves de correo y de IA, `CRON_SECRET`, contraseña de admin de empresas | Solo en variables de entorno de Render. Nunca en código, chats, capturas ni correos |
| **Confidencial** | Datos de clientes, facturas, fotos de casas, ubicación, datos de menores (Home Lab) | Solo accesible con sesión y rol; nunca públicos |
| **Interna** | Código, documentación | Repositorio **privado** |
| **Pública** | Páginas de privacidad y términos, landing | Sin restricción |

## 4. Control de acceso
- **Mínimo privilegio:** cada persona tiene el rol que necesita (User, Leader, Manager; en el ERP: worker, lead, boss, admin). Los permisos se comprueban en el servidor, no solo ocultando botones.
- **Aislamiento entre empresas:** cada empresa ve solo sus datos. El administrador de la plataforma entra a los datos de una empresa solo si su Manager le da **acceso de soporte** (24 o 72 h). Todo lo que se abre durante ese tiempo queda registrado y el Manager lo puede ver.
- **Altas y bajas:** al salir alguien de una empresa, su Manager lo quita el mismo día. Al menos cada 3 meses se revisa la lista de usuarios y de administradores de la plataforma.
- **Base de datos:** RLS activo en todas las tablas; solo el servidor (con la clave de servicio) lee y escribe. Ninguna clave de Supabase va al navegador.
- **Cuentas de servicios** (Render, Supabase, GitHub, Google, Namecheap, Anthropic, Resend): con verificación en dos pasos y sin cuentas compartidas.

## 5. Autenticación
- Contraseñas guardadas con bcrypt; PINs con hash (HMAC-SHA256). Nunca se envían por correo ni se muestran después de crearlos.
- Verificación en dos pasos (TOTP) disponible para todos y obligatoria si la empresa lo exige.
- Límites de intentos: 10 contraseñas fallidas por cuenta o 30 por IP en 15 min; 10 PINs fallidos por dispositivo en 10 min; 5 PINs por persona en 15 min.
- Sin contraseñas por defecto (no "admin", no "1234"): las de empresas se generan al azar.
- Cierre de sesión: por usuario (cambiar la contraseña cierra los demás dispositivos) y global (forzar cierre de sesión).

## 6. Gestión de secretos
- Los secretos viven solo en las variables de entorno de Render.
- Si un secreto aparece en una captura, un chat, un correo o en el repositorio, se considera **filtrado**: se regenera de inmediato (ver plan de incidentes).
- Rotación al menos una vez al año, y siempre que una persona con acceso deje la empresa.

## 7. Desarrollo y cambios
- Todo cambio va por git, con mensaje que explica qué y por qué.
- Antes de publicar se corren las pruebas automáticas (contratistas, autenticación, navegador); no se publica con pruebas fallando.
- Los cambios de base de datos se hacen con migraciones guardadas en `migrations/`.
- Después de cada cambio de esquema se revisan los **Security Advisors** de Supabase.
- Dependencias: revisión de actualizaciones de seguridad cada 3 meses.

## 8. Registro y monitoreo
- `audit_log`: inicios de sesión, intentos fallidos, bloqueos, cambios de PIN, roles y miembros, acceso de soporte, configuración y alta/edición de empresas. Incluye fecha, usuario e IP. **No se borra.**
- `contractor_mail_log`: cada correo enviado (o fallido) y su motivo.
- `contractor_support_log`: lo que abrió un administrador con acceso de soporte.
- `auth_report`: llamadas sin sesión (sirve para ver intentos de bots).
- Revisión: una vez al mes, mirar intentos fallidos y bloqueos inusuales en `audit_log`.

## 9. Protección de datos personales (ISO 27701)
- Se recoge solo lo necesario para el servicio (ver `/privacy`).
- **Ubicación:** solo con la app abierta; se borra automáticamente a los 90 días. Es el **único** dato que se borra solo. Facturas, órdenes, fotos, recibos, contactos y registros se conservan.
- Solicitudes de acceso, corrección o borrado: se responden en un máximo de 30 días. Si los datos son de una empresa cliente, se coordina con su Manager.
- **Menores (Home Lab):** solo los registra un padre o tutor; requiere sesión, y sus PINs van cifrados.
- No se venden datos, no se usan para publicidad ni para entrenar IA.

## 10. Cifrado
- En tránsito: solo HTTPS (HSTS activo).
- En reposo: cifrado del proveedor (Supabase/AWS).
- Contraseñas y PINs: hash, nunca texto plano.

## 11. Continuidad y respaldos
- La base de datos debe tener **respaldos automáticos diarios** (plan Pro de Supabase o superior).
- Una vez por trimestre, probar que un respaldo se puede restaurar.
- El código está en GitHub; la app se puede volver a desplegar en Render desde `main`.

## 12. Equipos
Los equipos desde donde se administran los servicios tienen bloqueo de pantalla, sistema actualizado y disco cifrado. No se guardan secretos en archivos sueltos.

## 13. Incumplimientos
Cualquier incumplimiento se trata como incidente (ver `respuesta-incidentes.md`) y puede llevar a quitar accesos.
