#!/bin/bash
# AI Framework Auto-Installer
# Ejecutado por SessionStart hook en cada inicio de sesión
# Instala el framework en el proyecto del usuario solo la primera vez

set -e

# VALIDACIÓN CRÍTICA: Verificar que CLAUDE_PROJECT_DIR esté correctamente configurado
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
	echo "ERROR: CLAUDE_PROJECT_DIR no está definido" >&2
	echo "DEBUG: PWD=$PWD" >&2
	echo "DEBUG: CLAUDE_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT" >&2
	exit 1
fi

if [ "$CLAUDE_PROJECT_DIR" = "/" ]; then
	echo "ERROR: CLAUDE_PROJECT_DIR no puede ser la raíz del sistema" >&2
	exit 1
fi

if [ ! -d "$CLAUDE_PROJECT_DIR" ]; then
	echo "ERROR: CLAUDE_PROJECT_DIR no es un directorio válido: $CLAUDE_PROJECT_DIR" >&2
	exit 1
fi

# Marker para detectar si ya está instalado
MARKER="$CLAUDE_PROJECT_DIR/.specify/.ai-framework-installed"

# Si ya está instalado, no hacer nada
if [ -f "$MARKER" ]; then
	exit 0
fi

# Copiar archivos del template al proyecto del usuario
# Flag -n: no sobrescribir si existe
# 2>/dev/null: silenciar errores si archivos ya existen

cp -rn "${CLAUDE_PLUGIN_ROOT}/template/.specify" "$CLAUDE_PROJECT_DIR/" 2>/dev/null || true
cp -rn "${CLAUDE_PLUGIN_ROOT}/template/.claude" "$CLAUDE_PROJECT_DIR/" 2>/dev/null || true
cp -n "${CLAUDE_PLUGIN_ROOT}/template/CLAUDE.md" "$CLAUDE_PROJECT_DIR/" 2>/dev/null || true
cp -n "${CLAUDE_PLUGIN_ROOT}/template/.mcp.json" "$CLAUDE_PROJECT_DIR/" 2>/dev/null || true

# Crear marker de instalación
mkdir -p "$CLAUDE_PROJECT_DIR/.specify"
echo "Installed on $(date)" >"$MARKER"

exit 0
