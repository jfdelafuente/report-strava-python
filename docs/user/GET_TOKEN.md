# Guía: Obtención de Tokens de Strava

**Versión**: 1.0.0
**Última actualización**: 3 de diciembre de 2025

---

## Resumen

Esta guía explica cómo obtener y gestionar los tokens de autenticación de Strava necesarios para usar **py-strava**. El script `01_get_token.py` automatiza todo el proceso de forma interactiva.

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración de la Aplicación en Strava](#configuración-de-la-aplicación-en-strava)
3. [Uso del Script](#uso-del-script)
4. [Modos de Operación](#modos-de-operación)
5. [Estructura del Archivo de Tokens](#estructura-del-archivo-de-tokens)
6. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. ✅ Una cuenta de Strava activa
2. ✅ Python 3.8 o superior instalado
3. ✅ El proyecto py-strava instalado (`pip install -e .`)
4. ✅ Los directorios necesarios creados (`mkdir -p bd data json`)

---

## Configuración de la Aplicación en Strava

### 1. Crear una Aplicación en Strava

1. Ve a [Strava API Settings](https://www.strava.com/settings/api)
2. Completa el formulario:
   - **Application Name**: `py-strava` (o el nombre que prefieras)
   - **Category**: `Data Analysis` o `Visualizer`
   - **Club**: Dejar vacío (opcional)
   - **Website**: `http://localhost` (o tu sitio web)
   - **Authorization Callback Domain**: `localhost`

3. Haz clic en **Create**

### 2. Obtener Credenciales

Después de crear la aplicación, obtendrás:

- **Client ID**: Un número (ej: `12345`)
- **Client Secret**: Una cadena alfanumérica (ej: `a1b2c3d4e5f6...`)

⚠️ **IMPORTANTE**: Guarda estas credenciales de forma segura. No las compartas públicamente.

### 3. Configuración Opcional - Variables de Entorno

Para mayor seguridad y comodidad, puedes configurar las credenciales como variables de entorno:

**En Linux/Mac:**

```bash
export STRAVA_CLIENT_ID="12345"
export STRAVA_CLIENT_SECRET="tu_client_secret_aqui"
```

**En Windows (CMD):**

```cmd
set STRAVA_CLIENT_ID=12345
set STRAVA_CLIENT_SECRET=tu_client_secret_aqui
```

**En Windows (PowerShell):**

```powershell
$env:STRAVA_CLIENT_ID="12345"
$env:STRAVA_CLIENT_SECRET="tu_client_secret_aqui"
```

---

## Uso del Script

### Modo Interactivo (Recomendado)

El modo más fácil de usar el script es ejecutarlo sin argumentos:

```bash
python scripts/01_get_token.py
```

El script te guiará paso a paso a través del proceso:

```plaintext
======================================================================
  OBTENCIÓN DE TOKENS DE STRAVA - MODO INTERACTIVO
======================================================================

ℹ️  Obtención de credenciales de Strava
   Las credenciales se pueden obtener de:
   https://www.strava.com/settings/api

📝 Ingresa tus credenciales de Strava:
   Client ID: 12345
   Client Secret: a1b2c3d4e5f6...

1. Generar código de autorización

   URL de autorización:
   https://www.strava.com/oauth/authorize?client_id=12345...

¿Abrir URL en el navegador? [s]:
```

### Flujo Completo

#### Paso 1: Ejecutar el Script

```bash
python scripts/01_get_token.py
```

#### Paso 2: Ingresar Credenciales

El script solicitará tu `Client ID` y `Client Secret` (o los tomará de las variables de entorno).

#### Paso 3: Autorizar la Aplicación

1. El script abrirá automáticamente tu navegador (o puedes copiar la URL)
2. Inicia sesión en Strava si es necesario
3. Haz clic en **Authorize** para permitir el acceso
4. Serás redirigido a una URL como:
   ```
   http://localhost/?state=&code=abc123def456...&scope=read,activity:read_all
   ```

#### Paso 4: Copiar el Código

1. Copia el valor del parámetro `code` de la URL (todo lo que está después de `code=` y antes de `&scope`)
2. Pégalo en el terminal cuando el script lo solicite

#### Paso 5: ¡Listo!

El script intercambiará el código por tokens y los guardará automáticamente en `json/strava_tokens.json`:

```plaintext
✅ Autenticación exitosa
✅ Tokens guardados en: json/strava_tokens.json

📋 Información del token:
   Token Type:     Bearer
   Access Token:   a1b2c3d4e5f6789...0123456789
   Refresh Token:  x9y8z7w6v5u4t3s...9876543210
   Expira:         2025-12-03 18:30:00 (5.9 horas)

👤 Información del atleta:
   Nombre:         Juan García
   ID:             12345678
```

---

## Modos de Operación

### 1. Modo Interactivo (Default)

Guía paso a paso para obtener tokens nuevos:

```bash
python scripts/01_get_token.py
```

**Casos de uso:**
- Primera vez usando la aplicación
- Generar un nuevo token
- El refresh_token ha expirado

---

### 2. Modo Verificación (`--verify`)

Verifica un token existente sin modificarlo:

```bash
python scripts/01_get_token.py --verify
```

**Salida esperada:**

```plaintext
======================================================================
  VERIFICAR TOKEN EXISTENTE
======================================================================

✅ Archivo encontrado: json/strava_tokens.json
✅ Estructura del token válida
✅ Token VÁLIDO
   Válido por 5.2 horas más

📋 Información del token:
   [Detalles del token...]
```

**Casos de uso:**
- Verificar si el token sigue válido
- Ver cuánto tiempo falta para que expire
- Comprobar la estructura del archivo

---

### 3. Modo Renovación (`--refresh`)

Renueva un token existente usando el `refresh_token`:

```bash
python scripts/01_get_token.py --refresh
```

**Salida esperada:**

```plaintext
======================================================================
  RENOVAR TOKEN
======================================================================

ℹ️  Renovando token...
✅ Token renovado exitosamente
✅ Tokens actualizados en: json/strava_tokens.json

📋 Información del token:
   [Nuevos tokens...]
```

**Casos de uso:**
- Token de acceso expirado
- Renovación proactiva antes de que expire
- Automatización (scripts, cron jobs)

---

### 4. Archivo Personalizado (`--token`)

Usa un archivo diferente al predeterminado:

```bash
python scripts/01_get_token.py --token ./config/mi_token.json
python scripts/01_get_token.py --verify --token ./tokens/prod.json
python scripts/01_get_token.py --refresh --token ./tokens/test.json
```

**Casos de uso:**
- Múltiples cuentas de Strava
- Diferentes entornos (dev, test, prod)
- Ubicaciones personalizadas

---

## Estructura del Archivo de Tokens

El archivo `json/strava_tokens.json` tiene la siguiente estructura:

```json
{
  "token_type": "Bearer",
  "expires_at": 1733248200,
  "expires_in": 21600,
  "refresh_token": "a1b2c3d4e5f6g7h8i9j0...",
  "access_token": "x9y8z7w6v5u4t3s2r1q0...",
  "client_id": "12345",
  "client_secret": "a1b2c3d4e5f6..."
}
```

### Descripción de Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `token_type` | String | Tipo de token (siempre "Bearer") |
| `expires_at` | Integer | Timestamp Unix de expiración |
| `expires_in` | Integer | Segundos hasta expirar (típicamente 21600 = 6 horas) |
| `refresh_token` | String | Token para renovar el access_token |
| `access_token` | String | Token de acceso a la API (válido ~6 horas) |
| `client_id` | String | ID del cliente de tu aplicación |
| `client_secret` | String | Secret del cliente de tu aplicación |

### ⚠️ Seguridad

- ❌ **NUNCA** subas este archivo a Git/repositorios públicos
- ✅ El archivo ya está en `.gitignore` para protegerlo
- ✅ Mantén `client_secret` y `refresh_token` seguros
- ✅ Revoca el acceso en Strava si sospechas compromiso

---

## Solución de Problemas

### Error: "Código de autorización requerido"

**Causa**: No se proporcionó el código de autorización.

**Solución**:
1. Asegúrate de autorizar la aplicación en Strava
2. Copia el código **completo** de la URL de redirección
3. El código debe tener ~40 caracteres

---

### Error: "Error de autenticación"

**Causa**: Código inválido, expirado, o credenciales incorrectas.

**Solución**:
1. Verifica que `client_id` y `client_secret` sean correctos
2. El código de autorización expira en ~10 minutos, genera uno nuevo
3. Asegúrate de que la Authorization Callback Domain sea `localhost`

---

### Error: "Archivo de tokens no encontrado"

**Causa**: No existe el archivo `json/strava_tokens.json`.

**Solución**:
1. Ejecuta el script en modo interactivo para crear uno nuevo:
   ```bash
   python scripts/01_get_token.py
   ```
2. O verifica que el directorio `json/` exista:
   ```bash
   mkdir -p json
   ```

---

### Error: "Token EXPIRADO"

**Causa**: El `access_token` ha expirado (normal después de ~6 horas).

**Solución**:
1. Renueva el token automáticamente:
   ```bash
   python scripts/01_get_token.py --refresh
   ```
2. O usa los comandos CLI que renuevan automáticamente:
   ```bash
   strava sync    # Renueva automáticamente si es necesario
   ```

---

### Error: "Refresh token inválido"

**Causa**: El `refresh_token` también ha expirado (raro, pero posible).

**Solución**:
1. Genera un nuevo token desde cero:
   ```bash
   python scripts/01_get_token.py
   ```
2. Autoriza nuevamente la aplicación en Strava

---

### Error: "Credenciales no configuradas"

**Causa**: No se proporcionaron `client_id` ni `client_secret`.

**Solución**:
1. Configura variables de entorno:
   ```bash
   export STRAVA_CLIENT_ID="12345"
   export STRAVA_CLIENT_SECRET="tu_secret"
   ```
2. O ingrésalas cuando el script lo solicite

---

### El navegador no se abre automáticamente

**Causa**: Problema con el módulo `webbrowser` o permisos.

**Solución**:
1. Cuando el script pregunte "¿Abrir URL en el navegador? [s]:", responde `n`
2. Copia manualmente la URL mostrada y ábrela en tu navegador

---

## Automatización

### Renovación Automática con Cron

Puedes automatizar la renovación del token con un cron job (Linux/Mac):

```bash
# Editar crontab
crontab -e

# Añadir línea para renovar cada 5 horas
0 */5 * * * cd /ruta/a/py-strava && python scripts/01_get_token.py --refresh
```

### Script de Renovación

Puedes crear un script wrapper para manejar errores:

```bash
#!/bin/bash
# renovar_token.sh

cd /ruta/a/py-strava
python scripts/01_get_token.py --refresh

if [ $? -eq 0 ]; then
    echo "✅ Token renovado exitosamente"
else
    echo "❌ Error al renovar token"
    # Enviar notificación, email, etc.
fi
```

---

## Integración con la CLI

Los comandos CLI (`strava sync`, `strava report`) **renuevan automáticamente** el token si ha expirado, por lo que normalmente no necesitas usar `01_get_token.py --refresh` manualmente.

**Flujo típico:**

```bash
# 1. Primera vez: obtener token
python scripts/01_get_token.py

# 2. Usar la CLI normalmente
strava sync      # Renueva automáticamente si es necesario
strava report

# 3. Solo si necesitas verificar manualmente
python scripts/01_get_token.py --verify
```

---

## Referencias

### Documentación Externa

- [Strava API Authentication](https://developers.strava.com/docs/authentication/)
- [Strava API Settings](https://www.strava.com/settings/api)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)

### Documentación del Proyecto

- [README.md](../../README.md) - Documentación principal
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guía de inicio rápido
- [SOLUCION_ERRORES.md](SOLUCION_ERRORES.md) - Solución de problemas

---

**Última actualización**: 3 de diciembre de 2025
**Versión del documento**: 1.0.0
