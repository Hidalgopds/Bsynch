# Proveedores (subprocesadores)

Servicios externos que guardan o procesan datos de BSynch. Antes de agregar uno nuevo: revisar su página de seguridad (que tenga SOC 2 o ISO 27001), sus términos de tratamiento de datos (DPA) y anotarlo aquí. También hay que actualizar la sección 4 de `/privacy`.

| Proveedor | Para qué | Datos que toca | Dónde | Notas |
|---|---|---|---|---|
| **Render** | Servidor de la app | Todo lo que pasa por la app; variables secretas | EE. UU. | Activar 2FA en la cuenta |
| **Supabase** (AWS us-east-1) | Base de datos | Todos los datos guardados | EE. UU. | RLS en todas las tablas. **Plan actual Free: sin respaldos automáticos** |
| **Anthropic** | Leer fotos de recibos y tickets | Solo la imagen del recibo | EE. UU. | Por su política comercial, no entrena con datos de la API (verificar en su página de privacidad) |
| **Resend** | Enviar facturas, estimados y alertas | Destinatarios y contenido del correo | EE. UU. | |
| **Google (Gmail SMTP)** | Correos del ERP | Destinatarios y contenido del correo | EE. UU. | Usar contraseña de aplicación, nunca la contraseña de la cuenta |
| **Namecheap Private Email** | Enviar desde el dominio de la empresa | Destinatarios y contenido del correo | | |
| **GitHub** | Código fuente | Código (sin secretos) | EE. UU. | **El repositorio debe ser privado** |
| **cdnjs (Cloudflare) / jsDelivr** | Librerías del navegador (QR, PDF, Excel, OCR) | Ninguno (solo descargan código) | Global | |
| **Intuit QuickBooks** (pendiente) | Sincronizar facturas | Facturas y clientes | EE. UU. | Regenerar el client secret que salió en una captura |
| **Stripe** (pendiente) | Pagos | Datos de pago (los maneja Stripe) | EE. UU. | |

**Revisión:** una vez al año, confirmar que cada proveedor sigue con su certificación vigente y que se sigue usando. Quitar los que no se usen.
