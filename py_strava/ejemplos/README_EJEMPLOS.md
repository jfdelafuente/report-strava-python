# Scripts de Ejemplo - py-strava

Este directorio contiene scripts de ejemplo para diferentes operaciones con la API de Strava.

---

## 📝 acces_token_strava.py

**Script mejorado para obtener el token inicial de Strava de forma segura e interactiva.**

### ✨ Características

- ✅ **Entrada interactiva**: No necesitas hardcodear credenciales
- ✅ **Validación completa**: Verifica credenciales y respuestas
- ✅ **Manejo de errores robusto**: Mensajes claros si algo falla
- ✅ **Logging profesional**: Seguimiento del proceso
- ✅ **Seguridad**: No guarda credenciales en el código
- ✅ **Documentación completa**: Instrucciones paso a paso

### 🚀 Cómo Usar

#### Paso 1: Crear una aplicación en Strava

1. Ve a https://www.strava.com/settings/api
2. Crea una nueva aplicación (My API Application)
3. Anota estos datos:
   - **Client ID**: número de tu aplicación
   - **Client Secret**: clave secreta

#### Paso 2: Obtener el código de autorización

Visita esta URL en tu navegador (reemplaza `YOUR_CLIENT_ID` con tu Client ID real):

```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all
```

Ejemplo:
```
https://www.strava.com/oauth/authorize?client_id=56852&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all
```

#### Paso 3: Autorizar la aplicación

1. Se abrirá una página de Strava pidiéndote autorización
2. Haz clic en "Authorize"
3. Serás redirigido a una página que no carga (es normal)
4. Copia el `code` de la URL:
   ```
   http://localhost/exchange_token?state=&code=ESTE_ES_TU_CODE&scope=read,activity:read_all
   ```

#### Paso 4: Ejecutar el script

```bash
# Desde la raíz del proyecto
python -m py_strava.ejemplos.acces_token_strava
```

El script te pedirá:
- **Client ID**: El número de tu aplicación
- **Client Secret**: Tu clave secreta
- **Authorization Code**: El código que copiaste de la URL

#### Paso 5: Verificar

El script:
1. Solicitará el token a Strava
2. Mostrará información del token (ocultando partes sensibles)
3. Guardará el token en `json/strava_tokens.json`
4. Verificará que se guardó correctamente

### 📋 Ejemplo de Ejecución

```
============================================================
OBTENER TOKEN INICIAL DE STRAVA
============================================================

Por favor, ingresa tus credenciales de Strava:
(Puedes encontrarlas en https://www.strava.com/settings/api)

Client ID: 56852
Client Secret: 6b229c286a12180a2acad07d23a6f43ae999d046
Authorization Code: 896509433675a143c7a61b819dd8f5294888a4d9

2025-11-26 15:45:00 - INFO - Solicitando token de acceso a Strava...
2025-11-26 15:45:01 - INFO - ✅ Token de acceso obtenido correctamente

============================================================
TOKENS OBTENIDOS
============================================================
Access Token: a1b2c3d4e5...xyz9876543
Refresh Token: f6g7h8i9j0...abc1234567
Expires At: 1732635900
Token Type: Bearer

Atleta: Juan Pérez
Username: juanperez
============================================================

2025-11-26 15:45:01 - INFO - ✅ Tokens guardados en: ./json/strava_tokens.json
2025-11-26 15:45:01 - INFO - ✅ Archivo de tokens verificado correctamente

============================================================
✅ PROCESO COMPLETADO EXITOSAMENTE
============================================================

Tus tokens han sido guardados en: ./json/strava_tokens.json

Próximos pasos:
1. Ejecuta: python -m py_strava.main
2. El programa usará estos tokens automáticamente
3. Los tokens se refrescarán automáticamente cuando expiren
============================================================
```

### ⚠️ IMPORTANTE

- **Ejecuta este script solo UNA VEZ** para obtener el token inicial
- Después usa `python -m py_strava.main` que refresca el token automáticamente
- **NUNCA subas el archivo `json/strava_tokens.json` a Git** (ya está en .gitignore)
- El código de autorización solo funciona UNA VEZ, si falla debes obtener uno nuevo

### 🔧 Solución de Problemas

**Error: "Bad Request" o 400**
- El código de autorización ya fue usado o expiró
- Obtén un nuevo código siguiendo el Paso 2

**Error: "Unauthorized" o 401**
- Client ID o Client Secret incorrectos
- Verifica tus credenciales en https://www.strava.com/settings/api

**Error: "No se pudo obtener el token"**
- Verifica tu conexión a internet
- Comprueba que copiaste bien el código de autorización

**Error: "El Client ID debe ser un número"**
- Asegúrate de copiar solo el número, sin espacios

---

## 📚 Otros Scripts de Ejemplo

### get_acces_token_strava.py

Script alternativo para obtener tokens (similar funcionalidad).

### refresh_token_strava.py

Ejemplo de cómo refrescar manualmente un token (no necesario, `main.py` lo hace automáticamente).

### strava_activities_1.py, strava_activities_2.py

Ejemplos de cómo obtener actividades de Strava.

### strava_kudos_one.py

Ejemplo de cómo obtener kudos de una actividad específica.

---

## 🎯 Flujo de Trabajo Recomendado

1. **Primera vez:**
   ```bash
   python -m py_strava.ejemplos.acces_token_strava
   ```

2. **Uso normal:**
   ```bash
   python -m py_strava.main
   ```

3. **Generar informes:**
   ```bash
   python -m py_strava.informe_strava
   ```

---

## 📖 Más Información

- [Documentación de Strava API](https://developers.strava.com/docs/getting-started/)
- [Guía de autenticación OAuth](https://developers.strava.com/docs/authentication/)
- [README principal del proyecto](../../README.md)
- [Guía de inicio rápido](../../INICIO_RAPIDO.md)

---

**¿Problemas?** Consulta [SOLUCION_ERRORES.md](../../SOLUCION_ERRORES.md)
