#!/usr/bin/env python3
"""
Validador de Slash Commands para Claude Code
Valida sintaxis YAML y campos opcionales
Stdlib only - sin dependencias externas
"""

import sys
import re
import os
from pathlib import Path

# Import shared validators to eliminate code duplication
from common_validators import (
    extract_frontmatter,
    parse_simple_yaml,
    validate_utf8_encoding,
)


def validate_command(file_path):
    """Valida un archivo de slash command"""
    errors = []
    warnings = []

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return [f"ERROR: Archivo no encontrado: {file_path}"], []

    # Validar UTF-8 encoding (using common validator for consistency)
    utf8_error = validate_utf8_encoding(file_path)
    if utf8_error:
        return [utf8_error], []

    # Leer contenido
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraer frontmatter (es opcional para commands, pero común)
    frontmatter_text = extract_frontmatter(content)

    if frontmatter_text:
        # Si hay frontmatter, validarlo
        try:
            fields = parse_simple_yaml(frontmatter_text)
        except Exception as e:
            errors.append(f"ERROR: Frontmatter YAML inválido: {e}")
            return errors, warnings

        # Validar campos opcionales
        if "description" not in fields:
            warnings.append(
                "WARNING: Se recomienda incluir 'description' en frontmatter"
            )

        if "allowed-tools" in fields:
            tools = fields["allowed-tools"]
            # Verificar formato de patrones (e.g., Bash(git add:*))
            if "Bash(" in tools:
                # Validar que los patrones Bash estén bien formados
                bash_patterns = re.findall(r"Bash\([^)]+\)", tools)
                for pattern in bash_patterns:
                    if not re.match(r"Bash\(.+\)", pattern):
                        errors.append(f"ERROR: Patrón Bash mal formado: {pattern}")
            # Verificar que no termine en coma
            if tools.strip().endswith(","):
                errors.append("ERROR: Campo 'allowed-tools' no debe terminar en coma")

        if "model" in fields:
            valid_models = ["sonnet", "opus", "haiku"]
            if fields["model"] not in valid_models:
                errors.append(
                    f"ERROR: 'model' debe ser uno de {valid_models}: {fields['model']}"
                )

        if "disable-model-invocation" in fields:
            value = fields["disable-model-invocation"].lower()
            if value not in ["true", "false"]:
                errors.append(
                    f"ERROR: 'disable-model-invocation' debe ser true o false: {value}"
                )
    else:
        warnings.append(
            "WARNING: No se encontró frontmatter YAML (opcional pero recomendado)"
        )

    # Validar contenido markdown
    body_start = content.find("---\n", 4) + 4 if frontmatter_text else 0
    body = content[body_start:].strip()

    if not body:
        errors.append("ERROR: No hay contenido markdown en el comando")

    # Verificar uso de parámetros ($1, $2, $ARGUMENTS)
    if "$1" in body or "$2" in body or "$ARGUMENTS" in body:
        # Si usa parámetros, debería tener argument-hint
        if frontmatter_text:
            fields = parse_simple_yaml(frontmatter_text)
            if "argument-hint" not in fields:
                warnings.append(
                    "WARNING: El comando usa parámetros pero no tiene 'argument-hint'"
                )

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Uso: validate_command.py <ruta-al-command.md>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    errors, warnings = validate_command(file_path)

    # Reportar resultados
    if errors:
        print(f"\n❌ ERRORES en {file_path}:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print(f"\n⚠️  ADVERTENCIAS en {file_path}:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors and not warnings:
        print(f"\n✅ {file_path} es válido")
        sys.exit(0)
    elif errors:
        sys.exit(1)  # Errores fatales
    else:
        sys.exit(0)  # Solo warnings, no fatal


if __name__ == "__main__":
    main()
