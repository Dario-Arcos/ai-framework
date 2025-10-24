#!/usr/bin/env python3
"""
Validador de Sub-Agents para Claude Code
Valida sintaxis YAML y campos requeridos
Stdlib only - sin dependencias externas
"""

import sys
import re
import os
from pathlib import Path


def extract_frontmatter(content):
    """Extrae frontmatter YAML del contenido markdown"""
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def parse_simple_yaml(yaml_content):
    """
    Parser simple de YAML para frontmatter (no requiere PyYAML)
    Solo maneja formato simple key: value
    """
    fields = {}
    for line in yaml_content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            fields[key] = value
    return fields


def validate_agent(file_path):
    """Valida un archivo de sub-agent"""
    errors = []
    warnings = []

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return [f"ERROR: Archivo no encontrado: {file_path}"], []

    # Leer contenido
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR: No se pudo leer el archivo: {e}"], []

    # Extraer frontmatter
    frontmatter_text = extract_frontmatter(content)
    if not frontmatter_text:
        errors.append(
            "ERROR: No se encontró frontmatter YAML válido (debe estar delimitado por ---)"
        )
        return errors, warnings

    # Parsear frontmatter
    try:
        fields = parse_simple_yaml(frontmatter_text)
    except Exception as e:
        errors.append(f"ERROR: Frontmatter YAML inválido: {e}")
        return errors, warnings

    # Validar campos requeridos
    if "name" not in fields:
        errors.append("ERROR: Campo 'name' requerido en frontmatter")
    else:
        # Validar formato de nombre
        name = fields["name"]
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(
                f"ERROR: 'name' debe usar snake-case (lowercase, hyphens): {name}"
            )
        if len(name) > 64:
            errors.append(f"ERROR: 'name' no puede exceder 64 caracteres: {len(name)}")

    if "description" not in fields:
        errors.append("ERROR: Campo 'description' requerido en frontmatter")
    else:
        desc = fields["description"]
        if len(desc) > 1024:
            errors.append(
                f"ERROR: 'description' no puede exceder 1024 caracteres: {len(desc)}"
            )
        # Sugerencia: incluir "PROACTIVELY" para auto-delegación
        if "PROACTIVELY" not in desc.upper() and "proactive" not in desc.lower():
            warnings.append(
                "WARNING: Considerar incluir 'PROACTIVELY' en description para auto-delegación"
            )

    # Validar campos opcionales
    if "model" in fields:
        valid_models = ["sonnet", "opus", "haiku", "inherit"]
        if fields["model"] not in valid_models:
            errors.append(
                f"ERROR: 'model' debe ser uno de {valid_models}: {fields['model']}"
            )

    if "tools" in fields:
        tools = fields["tools"]
        # Verificar que no tenga comillas alrededor
        if '"' in tools or "'" in tools:
            warnings.append(
                "WARNING: Campo 'tools' no debe tener comillas alrededor de los valores"
            )
        # Verificar que no termine en coma
        if tools.strip().endswith(","):
            errors.append("ERROR: Campo 'tools' no debe terminar en coma")

    # Validar que hay contenido markdown después del frontmatter
    body_match = re.search(r"^---\s*\n.*?\n---\s*\n(.+)", content, re.DOTALL)
    if not body_match or not body_match.group(1).strip():
        errors.append("ERROR: No hay contenido markdown después del frontmatter")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Uso: validate_agent.py <ruta-al-agent.md>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    errors, warnings = validate_agent(file_path)

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
