# Solución de Problemas SSL en Redes Corporativas

Este documento explica cómo resolver errores de certificados SSL al usar la API de Strava en entornos corporativos.

---

## 🔴 Error Común

```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: self signed certificate in certificate chain (_ssl.c:992)'))
```

Este error ocurre cuando:
- Estás en una **red corporativa** (como MASORANGE)
- Hay un **proxy corporativo** interceptando el tráfico HTTPS
- Los **certificados autofirmados** de la empresa no son reconocidos por Python

---

## ✅ Soluciones

### Opción 1: Desactivar Verificación SSL (Recomendado para pruebas)

La forma más rápida es usar el parámetro `--no-ssl`:

```powershell
# Al obtener el token inicial
python -m py_strava.ejemplos.acces_token_strava --no-ssl

# El script te pedirá:
# - Client ID
# - Client Secret
# - Authorization Code
```

**Ventajas:**
- ✅ Funciona inmediatamente
- ✅ No requiere configuración adicional
- ✅ Solución temporal para pruebas

**Desventajas:**
- ⚠️ Menos seguro (desactiva verificación SSL)
- ⚠️ Solo para redes de confianza

---

### Opción 2: Configurar Certificados Corporativos (Recomendado para producción)

Si necesitas mantener la seguridad SSL, configura los certificados de tu empresa:

#### Paso 1: Obtener el certificado corporativo

1. Contacta con tu departamento de IT
2. Solicita el archivo de certificado corporativo (formato `.pem` o `.crt`)
3. Guárdalo en una ubicación segura, por ejemplo:
   ```
   C:\Certificados\corporativo.pem
   ```

#### Paso 2: Configurar Python para usarlo

**Método A - Variable de entorno (temporal):**

```powershell
# PowerShell
$env:REQUESTS_CA_BUNDLE = "C:\Certificados\corporativo.pem"
python -m py_strava.ejemplos.acces_token_strava
```

**Método B - Variable de entorno (permanente):**

```powershell
# PowerShell (como administrador)
[System.Environment]::SetEnvironmentVariable(
    "REQUESTS_CA_BUNDLE",
    "C:\Certificados\corporativo.pem",
    "User"
)
```

**Método C - Configurar certifi:**

```powershell
# Instalar/actualizar certifi
pip install --upgrade certifi

# Ubicar donde está certifi
python -c "import certifi; print(certifi.where())"

# Agregar tu certificado al final de ese archivo
# Por ejemplo: C:\...\venv\Lib\site-packages\certifi\cacert.pem
```

---

### Opción 3: Actualizar Certifi

A veces simplemente actualizar certifi resuelve el problema:

```powershell
pip install --upgrade certifi requests urllib3
```

---

## 📋 Comparación de Opciones

| Opción | Seguridad | Facilidad | Recomendado Para |
|--------|-----------|-----------|------------------|
| `--no-ssl` | ⚠️ Baja | ✅ Muy Fácil | Pruebas rápidas, desarrollo |
| Certificados corporativos | ✅ Alta | ⚠️ Media | Producción, uso continuo |
| Actualizar certifi | ✅ Alta | ✅ Fácil | Primera opción a intentar |

---

## 🔧 Casos de Uso

### Caso 1: Prueba Rápida (Primera Vez)

```powershell
# Obtener token inicial con --no-ssl
python -m py_strava.ejemplos.acces_token_strava --no-ssl

# Una vez obtenido el token, el resto del proyecto no necesita esto
# porque el token se guarda en json/strava_tokens.json
```

### Caso 2: Uso Continuo en Red Corporativa

```powershell
# 1. Obtener certificado corporativo de IT
# 2. Configurar variable de entorno
$env:REQUESTS_CA_BUNDLE = "C:\Certificados\masorange.pem"

# 3. Usar normalmente
python -m py_strava.ejemplos.acces_token_strava
python -m py_strava.main
```

### Caso 3: Desarrollo en Casa, Producción en Oficina

```powershell
# En casa (sin proxy)
python -m py_strava.main

# En la oficina (con proxy)
$env:REQUESTS_CA_BUNDLE = "C:\Certificados\corporativo.pem"
python -m py_strava.main
```

---

## 🎯 Flujo de Trabajo Recomendado

### Para Obtener el Token Inicial

```powershell
# Opción A: Sin SSL (rápido)
python -m py_strava.ejemplos.acces_token_strava --no-ssl

# Opción B: Con certificados (seguro)
$env:REQUESTS_CA_BUNDLE = "C:\Certificados\corporativo.pem"
python -m py_strava.ejemplos.acces_token_strava
```

### Para Uso Diario

Una vez que tienes el token en `json/strava_tokens.json`, los otros scripts pueden tener el mismo problema. Para solucionarlo:

#### Solución Permanente: Configurar la Variable de Entorno

1. **Abre las Variables de Entorno de Windows:**
   - Presiona `Win + R`
   - Escribe `sysdm.cpl` y presiona Enter
   - Ve a la pestaña "Opciones avanzadas"
   - Haz clic en "Variables de entorno"

2. **Agregar la Variable:**
   - En "Variables de usuario", haz clic en "Nueva"
   - Nombre: `REQUESTS_CA_BUNDLE`
   - Valor: `C:\Certificados\corporativo.pem`
   - Haz clic en "Aceptar"

3. **Reinicia PowerShell y prueba:**
   ```powershell
   python -m py_strava.main
   ```

---

## 🐛 Troubleshooting

### Error: "No such file or directory: certificado.pem"

**Causa:** La ruta al certificado es incorrecta.

**Solución:**
```powershell
# Verificar que el archivo existe
Test-Path "C:\Certificados\corporativo.pem"
# Debe mostrar: True
```

### Error: "Unable to get local issuer certificate"

**Causa:** El certificado está incompleto o corrupto.

**Solución:**
1. Vuelve a descargar el certificado de IT
2. Asegúrate de que es el certificado raíz (root CA)
3. Verifica que está en formato PEM

### Sigue sin funcionar después de configurar el certificado

**Solución:**
```powershell
# 1. Limpiar variables de entorno
$env:REQUESTS_CA_BUNDLE = $null
$env:CURL_CA_BUNDLE = $null

# 2. Reinstalar certifi
pip uninstall certifi
pip install certifi

# 3. Intentar de nuevo con --no-ssl
python -m py_strava.ejemplos.acces_token_strava --no-ssl
```

---

## 📚 Información Adicional

### ¿Por qué ocurre esto en redes corporativas?

Las empresas (como MASORANGE) usan **proxies SSL** que:
1. Interceptan el tráfico HTTPS
2. Descifran la conexión con su propio certificado
3. Re-cifran la conexión con el certificado del destino

Python no reconoce estos certificados autofirmados por defecto, por eso falla la verificación SSL.

### ¿Es seguro usar `--no-ssl`?

**En redes corporativas de confianza:** Sí, razonablemente seguro
- El tráfico ya está siendo inspeccionado por el proxy corporativo
- Estás dentro de una red controlada

**En redes públicas (WiFi, etc.):** No, no es seguro
- Cualquiera podría interceptar tu tráfico
- Usa certificados corporativos en su lugar

### ¿Qué hace exactamente `--no-ssl`?

El parámetro `--no-ssl`:
- Pasa `verify=False` a la librería `requests`
- Desactiva la verificación de certificados SSL
- Suprime las advertencias de SSL inseguro
- Solo afecta a ese script específico

---

## 🔐 Mejores Prácticas

### ✅ RECOMENDADO

1. **Para desarrollo/pruebas:**
   ```powershell
   python -m py_strava.ejemplos.acces_token_strava --no-ssl
   ```

2. **Para producción:**
   ```powershell
   # Configurar certificado corporativo permanentemente
   [System.Environment]::SetEnvironmentVariable(
       "REQUESTS_CA_BUNDLE",
       "C:\Certificados\corporativo.pem",
       "User"
   )
   ```

### ❌ NO RECOMENDADO

- Modificar el código para siempre usar `verify=False`
- Ignorar errores SSL en producción
- Compartir certificados corporativos públicamente

---

## 📞 Soporte

### Si nada funciona:

1. **Contacta con IT:**
   - Solicita el certificado raíz corporativo
   - Pregunta si hay configuración especial para Python
   - Verifica configuración de proxy

2. **Alternativa temporal:**
   - Usa tu red doméstica sin proxy corporativo
   - Obtén el token desde casa
   - Úsalo en la oficina (el token ya no requiere SSL inicial)

3. **Revisa la documentación:**
   - [README.md](README.md)
   - [SOLUCION_ERRORES.md](SOLUCION_ERRORES.md)
   - [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

---

## 📝 Resumen Ejecutivo

**Problema:** Error SSL en redes corporativas con proxies

**Solución Rápida:**
```powershell
python -m py_strava.ejemplos.acces_token_strava --no-ssl
```

**Solución Permanente:**
```powershell
# Obtener certificado de IT
# Configurar variable de entorno
$env:REQUESTS_CA_BUNDLE = "C:\Certificados\corporativo.pem"
```

**Resultado:** ✅ Puedes usar la API de Strava sin errores SSL

---

**Última actualización:** 27 de noviembre de 2025

**¿Preguntas?** Consulta [README.md](README.md) o [SOLUCION_ERRORES.md](SOLUCION_ERRORES.md)
