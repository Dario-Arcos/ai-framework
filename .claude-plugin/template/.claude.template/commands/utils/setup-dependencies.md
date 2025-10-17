---
description: Install missing essential dependencies with platform detection
allowed-tools: Bash(*)
---

# Setup Dependencies

Instala dependencias esenciales faltantes para habilitar todas las features del framework.

## Execution

### 1. Detect Platform

Ejecutar:

```bash
os_type=`uname -s`

if [[ "$os_type" == "Darwin" ]]; then
    platform="darwin"
elif [[ "$os_type" == "Linux" ]]; then
    platform="linux"
else
    platform="unknown"
fi
```

### 2. Dependency Registry

Definir registry de dependencias (single source of truth):

```bash
# DEPENDENCY REGISTRY
# Format: tool_name|installer|platforms|purpose
# platforms: darwin, linux, all
# installer: brew, pip, npm, apt

DEPS=(
    "terminal-notifier|brew|darwin|Notificaciones de tareas completadas"
    "black|pip|all|Auto-formateo de código Python"
    # Future additions here (one line per dependency):
    # "playwright|npm|all|E2E testing automation"
    # "jq|brew|all|JSON processing"
    # "gh|brew|all|GitHub CLI operations"
)
```

### 3. Discover Missing Dependencies

Procesar registry y detectar faltantes:

```bash
missing=""
purposes=""

for entry in "${DEPS[@]}"; do
    IFS='|' read -r tool installer platforms purpose <<< "$entry"

    # Check if dependency applies to current platform
    if [[ "$platforms" == "all" ]] || [[ "$platforms" == "$platform" ]]; then
        # Check if tool is installed
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing="$missing $tool"
            purposes="$purposes\n   • $tool → $purpose"
        fi
    fi
done

# Trim leading space
missing=`echo "$missing" | xargs`
```

### 4. Display Status

Si `missing` está vacío:

```
✅ Todas las dependencias esenciales ya están instaladas.

No hay nada que instalar.
```

Terminar comando.

Si `missing` tiene contenido, mostrar:

```
📦 Dependencias a instalar:
   $missing

Estas herramientas habilitan:
$purposes

Plataforma: $platform
```

### 5. Confirm Installation

Preguntar:

```
¿Proceder con la instalación? (S/n):
```

Leer input del usuario.

Si respuesta NO es "S", "s", "Y", "y", o vacío:

```
❌ Instalación cancelada.

Instala manualmente según tu plataforma:
   macOS: brew install $missing
   Linux: pip install $missing (para Python packages)
```

Terminar.

### 6. Group by Installer

Agrupar dependencias por installer:

```bash
brew_deps=""
pip_deps=""
npm_deps=""

for entry in "${DEPS[@]}"; do
    IFS='|' read -r tool installer platforms purpose <<< "$entry"

    # Check if this tool is in missing list
    if [[ " $missing " == *" $tool "* ]]; then
        case "$installer" in
            brew) brew_deps="$brew_deps $tool" ;;
            pip) pip_deps="$pip_deps $tool" ;;
            npm) npm_deps="$npm_deps $tool" ;;
        esac
    fi
done

# Trim spaces
brew_deps=`echo "$brew_deps" | xargs`
pip_deps=`echo "$pip_deps" | xargs`
npm_deps=`echo "$npm_deps" | xargs`
```

### 7. Install by Package Manager

**Homebrew (macOS):**

```bash
if [ -n "$brew_deps" ]; then
    if ! command -v brew >/dev/null 2>&1; then
        echo "❌ Homebrew no instalado. Instalar: /bin/bash -c \"\`curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh\`\""
        exit 1
    fi

    echo "Instalando vía Homebrew: $brew_deps"
    brew install $brew_deps
fi
```

**pip (Python packages):**

```bash
if [ -n "$pip_deps" ]; then
    if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
        echo "❌ pip no instalado. Instalar Python 3.8+"
        exit 1
    fi

    echo "Instalando vía pip: $pip_deps"
    pip install $pip_deps 2>/dev/null || pip3 install $pip_deps
fi
```

**npm (Node packages):**

```bash
if [ -n "$npm_deps" ]; then
    if ! command -v npm >/dev/null 2>&1; then
        echo "❌ npm no instalado (viene con Node.js)"
        exit 1
    fi

    echo "Instalando vía npm: $npm_deps"
    npm install -g $npm_deps
fi
```

### 8. Verify Installation

Verificar todas las deps que intentamos instalar:

```bash
all_installed=true

for tool in $missing; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "✅ $tool instalado"
    else
        echo "❌ $tool falló"
        all_installed=false
    fi
done
```

### 9. Report Results

Si `all_installed` es true:

```
✅ Instalación completada

Todas las features del framework están habilitadas.
No necesitas reiniciar Claude Code.
```

Si `all_installed` es false:

```
⚠️ Algunas instalaciones fallaron

Verifica los errores arriba e instenta manual:
   macOS: brew install <tool>
   Python: pip install <tool>
   Node: npm install -g <tool>
```

## Extension Guide

Para agregar nuevas dependencias en el futuro:

1. Agregar línea al array DEPS:

   ```bash
   "tool_name|installer|platforms|purpose"
   ```

2. Soportado:
   - installers: brew, pip, npm, apt
   - platforms: darwin, linux, all
   - Automáticamente detecta, agrupa, e instala

## Important Notes

- Registry-driven: toda nueva dep es una línea
- Platform-agnostic: auto-detecta y filtra
- Installer-agnostic: agrupa por package manager
- Verification universal: loop sobre $missing
- NO shell=True (security compliant)
- Confirmación del usuario siempre
