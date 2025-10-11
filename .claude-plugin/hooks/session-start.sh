#!/bin/bash
# AI Framework Auto-Installer
# Ejecutado por SessionStart hook en cada inicio de sesión
# Instala el framework en el proyecto del usuario solo la primera vez

set -e

# IMPORTANTE: CLAUDE_PROJECT_DIR no está disponible en SessionStart hooks
# Usamos PWD que apunta al directorio donde Claude Code fue iniciado
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# Validación: verificar que PROJECT_DIR sea válido
if [ -z "$PROJECT_DIR" ]; then
	echo "ERROR: No se pudo determinar el directorio del proyecto" >&2
	exit 1
fi

if [ "$PROJECT_DIR" = "/" ]; then
	echo "ERROR: El directorio del proyecto no puede ser la raíz del sistema" >&2
	exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
	echo "ERROR: El directorio del proyecto no existe: $PROJECT_DIR" >&2
	exit 1
fi

# Marker para detectar si ya está instalado
MARKER="$PROJECT_DIR/.specify/.ai-framework-installed"

# Si ya está instalado, no hacer nada
if [ -f "$MARKER" ]; then
	exit 0
fi

# Copiar archivos del template al proyecto del usuario
# Flag -n: no sobrescribir si existe
# 2>/dev/null: silenciar errores si archivos ya existen

cp -rn "${CLAUDE_PLUGIN_ROOT}/template/.specify" "$PROJECT_DIR/" 2>/dev/null || true
cp -rn "${CLAUDE_PLUGIN_ROOT}/template/.claude" "$PROJECT_DIR/" 2>/dev/null || true
cp -n "${CLAUDE_PLUGIN_ROOT}/template/CLAUDE.md" "$PROJECT_DIR/" 2>/dev/null || true
cp -n "${CLAUDE_PLUGIN_ROOT}/template/.mcp.json" "$PROJECT_DIR/" 2>/dev/null || true

# Crear marker de instalación
mkdir -p "$PROJECT_DIR/.specify"
echo "Installed on $(date)" >"$MARKER"

exit 0
