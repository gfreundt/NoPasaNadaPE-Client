# Documento de Integración API NoPasaNadaPE v1

Este documento describe cómo realizar solicitudes via API al backend de nopasanadape.com. 

Orientado a terceros autorizados que necesiten realizar operaciones de alta y baja de clientes y consultas de información.

---

## 1. Información General

- **Base URL:** `nopasanadape.com/api/v1`
- **Formato:** JSON
- **Autenticación:** todas las solicitudes deben incluir un campo `token` en el cuerpo del request


### 1.1. Cabecera de Solicitud

| Campo          | Tipo   | Obligatorio | Descripción                  |
|----------------|--------|-------------|------------------------------|
| `Authorization`        | string | Sí          | Token de autenticación. Debe seguir el esquema RFC 6750: `Bearer [token]`.       |
| `Content-Type`        | string | Sí          | Debe ser `application/json` |

#### Ejemplo:

    curl -X POST nopasanadape.com/api/v1
         -H "Content-Type: application/json" 
         -H "Authorization: Bearer X5kP7dF8jA2qL9zMX5kP7dF8jA2qL9zM" 
         -d ...



### 1.2. Parámetros de Solicitud

| Campo          | Tipo   | Obligatorio | Descripción                  |
|----------------|--------|-------------|------------------------------|
| `usuario`        | string | Sí          | Usuario externo que hace la solicitud |
| `solicitud`     | string | Sí          | Tipo de solicitud que se hace              |
| `clientes`      | array  | depende del tipo de solicitud         | Listado de clientes          |


### 1.3. Cabecera de Respuesta

    ninguna

### 1.4. Parámetros de Respuesta
| Campo | Tipo |  Descripción |
| :--- | :--- | :--- 
| `id_solicitud` | int |  Código único generado para la solcitud. |  |
| `timestamp` | fecha |  Hora de procesamiento. `YYYY-MM-DD hh:mm:ss.dddddd`.|
| `resultados` | array |  Respuesta a la solicitud. Varía según tipo de solicitud.|



### 1.5. Códigos HTTP de Respuesta

| Código | Descripción                  |
|--------|------------------------------|
| 200    | Operación exitosa            |
| 207    | Resultado mixto (éxitos y fallos) |
| 400    | Error de validación          |
| 401    | No autenticado               |
| 404    | Solicitud inválida           |
| 500    | Error interno                |

---


## 2. Descripción de Campos


## 2.1. Token

Se debe utilizar el token alfanumérico proporcionado por nopasanadape.com.

### Ejemplo de respuesta si falla validación:
```json
{
    "id_solicitud": 30,
    "resultados":  {
        "error": "Token incorrecto."
        },
    "timestamp": "2025-12-15 15:45:33.187130"
    }
```

---
## 2.2. Usuario

Código establecido de común acuerdo entre el cliente externo y nopasanadape para identificar al colaborador del cliente externo que hace la solicitud.

El campo `usuario` no tiene validaciones.

### Ejemplo de respuesta si no se incluye usuario:
```json
{
    "id_solicitud": 34,
    "resultados": {
        "error": "Usuario requerido."
        },
    "timestamp": "2025-12-15 16:16:31.543746"}
```

---

## 2.3. Solicitud

Representa la acción solicitada por el usuario para ser ejecutada por la API. Las alternativas son:

- `alta`
- `baja`
- `clientes_autorizados`
- `mensajes_enviados`

### Ejemplo de respuesta si no se incluye solicitud o no es reconocida:
```json
{
    "id_solicitud": 34,
    "resultados": {
        "error": "Solicitud incorrecta."
        },
    "timestamp": "2025-12-15 16:16:31.543746"}
```


### 2.3.1. Solicitud de Alta

Activa uno o más clientes autorizados en el sistema.



| Campo | Tipo | Obligatorio | Descripción | Restricciones |
| :--- | :--- | :--- | :--- | :--- |
| `nombre` | string | No | Nombre completo del cliente. | Largo: Minimo: 5, Maximo:50. No debe contener caracteres especiales. |
| `tipo_documento` | string | No | Tipo de documento de identidad. | Debe ser uno de: `DNI`, `CE`, `PASAPORTE`. |
| `numero_documento` | string | No | Número de documento de identidad. | Cadena alfanumérica. La longitud y formato varían según el `tipo_documento`. |
| `celular` | string | No | Número de teléfono de contacto. | Numérico. Debe tener exactamente 9 dígitos. |
| `codigo_externo` | string | Sí | Código único de identificación del cliente en el sistema externo. | Cadena alfanumérica. No se valida el formato. |
| `perfil` | string | Sí | Código del perfil del cliente para futuras segmentaciones | Cadena alfanumérica. No se valida el formato. |
| `correo` | string | Sí | Dirección de correo electrónico. | usuario@dominio.com |

El array de `clientes` no puede estar vacío.

### Ejemplo de Solicitud

```json
{   
    "solicitud": "alta",
    "usuario": "MAQ-001",
    "clientes": [
        { 
            "nombre": "Juan Pérez",
            "tipo_documento": "DNI",
            "numero_documento": "12345678",
            "celular": "987654321",
            "codigo_externo": "CLI-001", 
            "perfil": "VIP3",
            "correo": "juan.perez@dominio.com"
            },
        {
            "nombre": "",
            "tipo_documento": "CE",
            "numero_documento": "0123456780",
            "celular": "",
            "codigo_externo": "CLI-001",
            "perfil": "REGULAR7",
            "correo": "jose.lopez@dominio.com"
            }
        ]
    }

```

### 2.3.2. Respuesta de Alta

El campo `resultados` es un array con elementos:

| Campo | Tipo | Descripción | Subestructura |
| :--- | :--- | :--- | :--- |
| `cuenta_exitos` | int | Cantidad de registros procesados correctamente. | -
| `cuenta_fallos` | int | Cantidad de registros no procesados|-
| `exitos` | array | Lista de registros procesados correctamente| Arrays con campos `correo` e `indice`.
| `fallos` | string | Lista de registros no procesados | Arrays con lista de `errores` en proceso e `indice`.

### Ejemplo de Respuesta
```json
{
    "id_solicitud": 37,
    "resultados": {
        "cuenta_exitos": 1,
        "cuenta_fallos": 1,
        "exitos": [
            {"correo": "juan.perez@dominio.com",
             "indice": 0
        }
             ],
        "fallos": [
            {"errores":
                [
                    "Numero de Documento Invalido."
            ],
            "indice": 1
        }
            ]
        },
 "timestamp": "2025-12-15 16:22:40.255584"
 }
```

### 2.3.3. Solicitud de Baja

Elimina clientes autorizados del sistema según su correo electrónico.

| Campo | Tipo | Obligatorio | Descripción | Restricciones |
| :--- | :--- | :--- | :--- | :--- |
| `correo` | string | Sí | Dirección de correo electrónico. | Debe cumplir con el formato estándar de email (ej: `usuario@dominio.com`). |

El array de `clientes` no puede estar vacío.

### Ejemplo de Request
```json
{
"token": "TOKEN_EXTERNO",
"solicitud": "baja",
"usuario": "admin",
"clientes": [
                {
                "correo": "juan.perez@dominio.com"
                },
                {
                "correo": "jose.lopez@dominio.com"
                }
    ]
}
```

### 2.3.4. Respuesta de Baja

El campo `resultados` es un array con elementos:

| Campo | Tipo | Descripción | Subestructura |
| :--- | :--- | :--- | :--- |
| `cuenta_exitos` | int | Cantidad de registros procesados correctamente. | -
| `cuenta_fallos` | int | Cantidad de registros no procesados|-
| `exitos` | array | Lista de registros procesados correctamente| Arrays con campos `correo` e `indice`.
| `fallos` | string | Lista de registros no procesados | Arrays con lista de `errores` en proceso e `indice`.


### Ejemplo de Respuesta
```json
{
    "id_solicitud": 38,
    "resultados": {
        "cuenta_exitos": 0,
        "cuenta_fallos": 1,
        "exitos": [],
        "fallos": [
            {   "errores": [
                    "Correo no encontrado."
                    ],
                "indice": 0
                }
            ]
        }
    }
```
### 2.3.5. Consulta de Mensajes Enviados

Obtiene los mensajes enviados dentro de un rango de fechas.

| Campo | Tipo de Dato | Obligatorio | Descripción | Formato |
| :--- | :--- | :--- | :--- | :--- |
| `fecha_desde` | string | No | Fecha inicial | YYYY-MM-DD |
| `fecha_hasta` | string| No | Fecha final | YYYY-MM-DD |

El array de `clientes` puede no existir o estar vacío.

### Ejemplos de Request

```json
{
"token": "TOKEN_EXTERNO",
"solicitud": "mensajes_enviados",
"usuario": "MAQ-003"
}
```

```json
{
"token": "TOKEN_EXTERNO",
"solicitud": "mensajes_enviados",
"usuario": "MAQ-002",
"fecha_desde": "2024-01-01",
"fecha_hasta": "2024-12-31"
}
```
### 2.3.6. Respuesta de Consulta de Mensajes Enviados

El campo `resultados` es un array con dos elementos:
- `cuenta`: un int con el total de registros devueltos
- `data`: 

| Campo | Tipo | Descripción | Formato |
| :--- | :--- | :--- | :--- |
| `direccion_correo` | string | Dirección de correo al que se envió el mensaje. | usario@dominio.com
| `timestamp_envio` | string | Hora en que se envió el mensaje | `YYYY-MM-DD hh:mm:ss.dddddd`
| `respuesta_mensaje` | string | Respuesta del servidor al enviar mensaje | `ok` / `error`
| `asunto` | string | Asunto del correo enviado | -
| `tipo_mensaje` | string | Tipo de mensaje enviado | `boletin` / `alerta`

### Ejemplo de Respuesta
```json
{
    "id_solicitud": 304,
    "timestamp": 2025-12-17 09:12:56.137459,
    "resultados": {
        "cuenta": 3,
        "data": [
            {
                "direccion_correo": "juna66@kudimi.com",
                "timestamp_envio": "2025-12-14 19:57:41.077390",
                "respuesta_mensaje": "ok",
                "asunto": "Tu Boletín de No Pasa Nada PE - Diciembre 2025",
                "tipo_mensaje": "boletin"
                },
            {
                "direccion_correo": "pepe093@kudimi.com",
                "timestamp_envio": "2025-12-14 20:57:27.320659",
                "respuesta_mensaje": "ok",
                "asunto": "Tienes una Alerta de No Pasa Nada PE",
                "tipo_mensaje": "alerta"
                },
            {
                "direccion_correo": "novite7175@kudimi.com",
                "timestamp_envio": "2025-12-14 21:00:04.890544",
                "respuesta_mensaje": "error",
                "asunto": "Tu Boletín de No Pasa Nada PE - Diciembre 2025",
                "tipo_mensaje": "boletin"
                }
            ]
        }
    }
```
### 2.3.7. Consulta de Clientes Autorizados

Obtiene la información actual de la lista de clientes autorizados y si se han inscrito en el servicio. Es solamente la informacion enviada al momento del alta, no la ingresada por el cliente al momento de suscribirse.

El array de `clientes` puede no existir o estar vacío.

### Ejemplo de Request

```json
{
    "solicitud": "clientes_autorizados",
    "usuario": "MAQ-003"
    }
```
### 2.3.8. Respuesta de Consulta de Clientes Autorizados

El campo `resultados` es un array con dos elementos:
- `cuenta`: un int con el total de registros devueltos
- `data`: 

| Campo | Tipo | Descripción | Formato |
| :--- | :--- | :--- | :--- |
| `id_solicitud` | int | Id de solicitud devuelta al activar cliente. | -
| `correo` | string | Dirección de correo activada. | usario@dominio.com
| `codigo_cliente` | string | Código del externo con que se activó al cliente | -
| `celular` | string | Celular activado | 9 dígitos
| `tipo_documento` | string | Tipo de documento activado | `DNI` / `CE` / `PASAPORTE`
| `numero_documento` | string | Tipo de documento activado | Alfanumerico
| `perfil` | string | Perfil con el que se activó al cliente. | Alfanumerico
| `timestamp_creado` | string | Hora en que se activó al cliente | `YYYY-MM-DD hh:mm:ss.dddddd`
| `nombre` | string | Nombre con el que se activó al cliente. | Solo caracteres alfabeticos
| `suscrito` | bool | Cliente completó proceso de suscripcion | `true` / `false`

### Ejemplo de Respuesta
```json
{
    "id_solicitud": 304,
    "timestamp": 2025-12-17 09:12:56.137459,
    "resultados": {
        "cuenta": 5,
        "data": [
            {
                "celular": "",
                "codigo_cliente": "MAQ-007",
                "correo": "lucho@gmail.com",
                "id_solicitud": 5,
                "nombre": "Luis Caceres",
                "numero_documento": "10025687",
                "perfil": "VIP9",
                "timestamp_creado": "2025-12-10 23:08:23.771669",
                "tipo_documento": "DNI",
                "suscrito": true
                },
            {
                "celular": "",
                "codigo_cliente": "MAQ-2137",
                "correo": "juan@correo.com.pe",
                "id_solicitud": 16,
                "nombre": "",
                "numero_documento": "",
                "perfil": "REGULAR3",
                "timestamp_creado": "2025-12-11 23:08:42.250366",
                "tipo_documento": "",
                "suscrito": false
                }
            ]  
        }
    }
```

---
**Código de Documento:** APIv1-001.v01  |  **Fecha de Emisión:** Diciembre 2025


