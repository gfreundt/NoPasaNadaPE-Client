# 🧩 Guía de Integración de API NoPasaNadaPE - Maquinarias S.A.

**Versión:** 1.0  
**Base Endpoint:** `https://nopasanadape.com/maquinarias/api/v1`  
**Método:** `POST`  
**Formato:** `JSON`  
**Codificación:** `UTF-8`

---

## 🧾 1. Descripción General

La API de **NoPasaNadaPE - Maquinarias** permite integrar sistemas externos para realizar operaciones de **alta**, **baja** o **consulta de información** de usuarios dentro de nuestra plataforma.  

Todas las solicitudes deben realizarse mediante el protocolo **HTTPS** para garantizar la seguridad de los datos.

---

## 📤 2. Estructura del Request

**Método:** `POST`  
**URL:** `https://nopasanadape.com/maquinarias/api/v1`  
**Encabezados Requeridos:**

```http
Content-Type: application/json
```

**Ejemplo de Petición Completa:**

```http
POST /maquinarias/api/v1 HTTP/1.1
Host: nopasanadape.com
Content-Type: application/json
```

**Cuerpo (Body):**

```json
{
  "token": "token_seguridad",
  "usuario": "codigo_usuario_maquinarias",
  "solicitud": "alta",
  "usuarios": [
    {
      "correo": "usuario@ejemplo.com"
    }
  ]
}
```

---

## ⚙️ 3. Parámetros del Request

| Campo       | Tipo     | Obligatorio | Descripción                                                                 |
|--------------|----------|--------------|------------------------------------------------------------------------------|
| `token`      | String   | ✅           | Token de seguridad proporcionado por NoPasaNadaPE para autenticar la solicitud. |
| `usuario`    | String   | ✅           | Código único del usuario o empresa que realiza la solicitud.                  |
| `solicitud`  | String   | ✅           | Tipo de operación: `"alta"`, `"baja"` o `"info"`.                            |
| `usuarios`   | Array    | ✅           | Lista de usuarios a procesar.                                               |
| `correo`     | String   | ✅ (por usuario) | Correo electrónico del usuario asociado a la operación.                    |

---

## 🧠 4. Ejemplos de Solicitudes

### ➕ Alta de usuario
```json
{
  "token": "1234567890abcdef",
  "usuario": "MAQ001",
  "solicitud": "alta",
  "usuarios": [
    {
      "correo": "nuevo_usuario@empresa.com"
    }
  ]
}
```

### ➖ Baja de usuario
```json
{
  "token": "1234567890abcdef",
  "usuario": "MAQ001",
  "solicitud": "baja",
  "usuarios": [
    {
      "correo": "usuario_baja@empresa.com"
    }
  ]
}
```

### ℹ️ Consulta de Información
```json
{
  "token": "1234567890abcdef",
  "usuario": "MAQ001",
  "solicitud": "info",
  "usuarios": []
}
```

---

## ✅ 5. Ejemplo de Respuesta Exitosa

### 🔸 Alta / Baja

```json
{
  "status": "ok",
  "mensaje": "Operación exitosa",
  "data": [
    {
    "correo": "nuevo_usuario@empresa.com",
    "procesado_en": "2025-10-28T17:30:25-05:00"
    }
  ]
}
```

> *Nota:* El campo `procesado_en` utiliza el formato **ISO 8601**, incluyendo la zona horaria local (`-05:00` para Perú).

---

### 🔸 Info

```json
{
  "status": "ok",
  "mensaje": "Operación exitosa",
  "data": [
    {
    "correo": "nuevo_usuario@empresa.com",
    "procesado_en": "2025-10-28T17:30:25-05:00",
    "inscrito": true|false
    }
  ]
}
```

> *Nota:* El campo `procesado_en` utiliza el formato **ISO 8601**, incluyendo la zona horaria local (`-05:00` para Perú).

---

## ❌ 6. Ejemplos de Errores

### 🔸 Token Inválido
```json
{
  "status": "error",
  "mensaje": "Token inválido"
}
```

### 🔸 Formato Incorrecto
```json
{
  "status": "error",
  "mensaje": "Formato de solicitud equivocado"
}
```

---

## 🔢 7. Códigos de Respuesta HTTP

La API devuelve diferentes códigos de estado HTTP según el resultado de la solicitud:

| Código | Significado | Descripción |
|--------|--------------|--------------|
| **200 OK** | ✅ Éxito | La solicitud fue procesada correctamente. El cuerpo contendrá los detalles de la operación realizada. |
| **400 Bad Request** | ❌ Error de solicitud | El formato del JSON es incorrecto, faltan campos obligatorios o la `solicitud` no es válida. |
| **401 Unauthorized** | 🚫 Token inválido | El `token` de seguridad no es válido o el usuario no está autorizado. |
| **500 Internal Server Error** | ⚠️ Error del servidor | Ocurrió un problema inesperado en el servidor al procesar la solicitud. |

---

## 📅 8. Campos Presentes en las Respuestas

| Campo          | Tipo   | Descripción |
|----------------|--------|--------------|
| `status`       | String | Indica el resultado de la operación (`ok` o `error`). |
| `mensaje`      | String | Describe el resultado o el motivo del error. |
| `procesado_en` | String | Fecha y hora de procesamiento en formato [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601). |

---

## 🛠️ 9. Recomendaciones Técnicas

- Utilizar siempre **HTTPS**.  
- Incluir el encabezado `Content-Type: application/json`.  
- No agregar campos adicionales no documentados.  
- Mantener en secreto el **token de seguridad**.  
- Validar siempre las respuestas antes de procesar la información.  
- Controlar los códigos HTTP para manejar errores correctamente en el cliente.  

---

© 2025 **NoPasaNadaPE** — Integraciones de Maquinarias API v1
