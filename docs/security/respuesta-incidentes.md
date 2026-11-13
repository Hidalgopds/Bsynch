# Plan de respuesta a incidentes

**Versión:** 1.0 · **Fecha:** 13 de noviembre de 2026 · **Responsable:** dueño de la plataforma

Un **incidente** es cualquier cosa que ponga en riesgo datos o el servicio: una clave filtrada, una cuenta tomada, datos vistos por quien no debía, la app caída o datos borrados por error.

## 1. Gravedad
| Nivel | Ejemplos | Tiempo para empezar |
|---|---|---|
| **Crítico** | Datos de clientes o de menores expuestos; clave de servicio de Supabase filtrada; base de datos borrada | De inmediato |
| **Alto** | Cuenta de Manager o admin tomada; otra clave filtrada (correo, IA, QuickBooks) | Mismo día |
| **Medio** | Muchos intentos de acceso fallidos; un usuario normal comprometido | 24 h |
| **Bajo** | Error que no expuso datos | Próxima revisión |

## 2. Pasos (para cualquier incidente)
1. **Detectar y anotar:** qué se vio, cuándo y quién lo reportó. Anotar todo en la bitácora (sección 5).
2. **Contener:** cortar el acceso (ver las guías de la sección 3). Primero se contiene y después se investiga.
3. **Investigar:** revisar `audit_log`, `contractor_support_log`, `contractor_mail_log`, los logs de Render y los de Supabase. Determinar qué datos, de qué empresa y de qué personas.
4. **Corregir:** arreglar la causa (código, configuración o permisos), con pruebas.
5. **Recuperar:** restaurar desde un respaldo si hace falta y confirmar que todo funciona.
6. **Notificar** (sección 4).
7. **Aprender:** en los 7 días siguientes, anotar qué falló y qué control se agrega para que no se repita.

## 3. Guías rápidas

**Clave o secreto filtrado** (en una captura, chat, correo o el repositorio)
1. Regenerar la clave en el servicio (Supabase → Settings → API; Anthropic; Resend; Google/Namecheap; QuickBooks; `SECRET_KEY` y `CRON_SECRET` en Render).
2. Ponerla en las variables de entorno de Render y redesplegar.
3. Si se cambió `SECRET_KEY`, todas las sesiones se cierran solas: es lo esperado.
4. Si estuvo en el repositorio: hacerlo privado y borrar el secreto del historial (por ejemplo con `git filter-repo`), aunque ya se haya regenerado.

**Cuenta tomada**
1. Cambiar la contraseña de esa cuenta (eso cierra sus demás sesiones), o quitarla de la empresa.
2. Si es admin: usar "forzar cierre de sesión" global.
3. Revisar en `audit_log` qué hizo esa cuenta y desde qué IP.
4. Activar la verificación en dos pasos obligatoria para la empresa.

**Datos expuestos**
1. Cerrar la ruta o el permiso que los expuso.
2. Determinar qué registros, de qué empresa y de cuántas personas.
3. Pasar a la notificación.

**App caída o datos borrados**
1. Revisar el estado de Render y de Supabase.
2. Volver a la versión anterior en Render (Rollback) si el problema vino de un despliegue.
3. Restaurar desde el respaldo de Supabase si se perdieron datos.

## 4. Notificaciones
- **Empresa afectada:** avisar a su Manager lo antes posible, como máximo en 72 horas desde que se confirma el incidente: qué pasó, qué datos, qué se hizo y qué debe hacer la empresa.
- **Personas afectadas (ley de Texas, Bus. & Com. Code §521.053):** si se expuso información personal sensible, avisar a cada persona sin demora y como máximo a los 60 días. Si son 250 o más residentes de Texas, avisar también al Fiscal General de Texas (en un máximo de 30 días). Personas en otros estados pueden tener otros plazos. **Consultar con un abogado antes de notificar.**
- **Proveedores:** si el incidente viene de un proveedor, pedirle su informe.

## 5. Bitácora de incidentes
Copiar esta tabla por cada incidente:

| Campo | Valor |
|---|---|
| Fecha y hora detectado | |
| Reportado por | |
| Gravedad | |
| Qué pasó | |
| Datos o personas afectadas | |
| Contención (qué y cuándo) | |
| Causa | |
| Corrección | |
| Notificaciones (a quién y cuándo) | |
| Lección y control nuevo | |
| Cerrado (fecha) | |

## 6. Contactos
| Quién | Cómo |
|---|---|
| Responsable de la plataforma | (completar teléfono y correo) |
| Abogado | (completar) |
| Render | dashboard.render.com → Support |
| Supabase | supabase.com/dashboard → Support |
| Fiscal General de Texas (aviso de brechas) | texasattorneygeneral.gov |
