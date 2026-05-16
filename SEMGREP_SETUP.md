# Semgrep - Configuración de Seguridad

## Overview

Este proyecto incluye integración con Semgrep para escaneo de seguridad estático tanto en CI/CD como MCP para asistencia durante desarrollo.

## GitHub Actions (ya configurado)

Semgrep corre automáticamente en el workflow de CI/CD en el job `security`:

```yaml
- name: Run Semgrep Security Scan
  uses: returntocorp/semgrep-action@v1
```

El escaneo usa la configuración `auto` que selecciona reglas apropiadas para Python/FastAPI.

### Para habilitar análisis avanzado (opcional)

1. Regístrate gratis en https://semgrep.dev
2. Crea un token en Settings > API
3. Agrega el token como secret en GitHub: `SEMGREP_APP_TOKEN`

Sin token, Semgrep corre en modo Community (menos reglas).

## MCP - Para escaneo durante desarrollo

### Instalación del cliente MCP

#### Claude Desktop (Windows)
```powershell
# Ubicación: %APPDATA%/Claude/mcp.json
```

Crea el archivo con:
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "npx",
      "args": ["-y", "@semgrep/mcp"]
    }
  }
}
```

#### opencode
```powershell
# Ubicación: ~/.config/opencode/mcp.json
```

#### VS Code / Cursor
Agrega la configuración en `.cursor/mcp.json` o en settings.json

### Alternativa: Ejecución directa (sin MCP)

Si no tienes el MCP configurado, puedes ejecutar Semgrep directamente:

```bash
# Instalar
pip install semgrep

# Escaneo básico
semgrep scan --config=auto ./app/

# Escaneo con reglas específicas
semgrep scan --config=r/owasp-top-10 ./app/
semgrep scan --config=r/frameworks ./app/

# Salida JSON para automatización
semgrep scan --config=auto --json --output=semgrep-results.json ./app/
```

## Reglas relevantes para FastAPI/Python

| Regla | Descripción |
|-------|-------------|
| `auto` | Selección automática basada en lenguaje |
| `r/owasp-top-10` | Top 10 OWASP |
| `r/frameworks` | Frameworks (Django, Flask, FastAPI) |
| `r/python` | Solo Python |

## Ejemplos de vulnerabilidades detectadas

- SQL Injection
- Hardcoded passwords/secrets
- XSS (Cross-Site Scripting)
- Weak cryptography (MD5, DES)
- Insecure file operations
- Path traversal
- Command injection

## Recursos

- Documentación: https://semgrep.dev/docs/
- Reglas: https://semgrep.dev/r/
- Slack: https://go.semgrep.dev/slack