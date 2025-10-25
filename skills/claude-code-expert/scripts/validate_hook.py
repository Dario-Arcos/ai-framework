#!/usr/bin/env python3
"""
Validador de Hooks para Claude Code
Valida sintaxis Python, estructura JSON I/O, y configuración hooks.json
Stdlib only - sin dependencias externas
"""

import sys
import os
import json
import ast


def validate_python_syntax(file_path):
    """Valida que el archivo Python tenga sintaxis correcta"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"ERROR de sintaxis Python: {e}"


def validate_hook_script(file_path):
    """Valida un script de hook Python"""
    errors = []
    warnings = []

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return [f"ERROR: Archivo no encontrado: {file_path}"], []

    # Validar sintaxis Python
    valid, syntax_error = validate_python_syntax(file_path)
    if not valid:
        errors.append(syntax_error)
        return errors, warnings

    # Leer contenido
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar shebang
    if not content.startswith("#!/usr/bin/env python3"):
        warnings.append("WARNING: Se recomienda shebang '#!/usr/bin/env python3'")

    # Verificar imports de stdlib only
    import_pattern = r"^import\s+(\w+)|^from\s+(\w+)"
    stdlib_modules = {
        "sys",
        "os",
        "json",
        "subprocess",
        "pathlib",
        "re",
        "datetime",
        "time",
        "collections",
        "itertools",
    }
    external_imports = []

    for line in content.split("\n"):
        match = re.match(import_pattern, line.strip())
        if match:
            module = match.group(1) or match.group(2)
            if module and module not in stdlib_modules:
                # Podría ser módulo externo
                if not module.startswith("_"):  # Ignorar módulos internos
                    external_imports.append(module)

    if external_imports:
        errors.append(
            f"ERROR: Hook usa dependencias externas (solo stdlib): {', '.join(external_imports)}"
        )

    # Verificar stdin/stdout patterns
    if "sys.stdin" not in content:
        warnings.append("WARNING: Hook debería leer de sys.stdin para recibir JSON")

    if "sys.stdout" not in content and "print(" not in content:
        warnings.append(
            "WARNING: Hook debería escribir a sys.stdout para retornar datos"
        )

    # Verificar exit codes
    if "sys.exit(" not in content:
        warnings.append(
            "WARNING: Hook debería usar sys.exit(código) para indicar resultado"
        )

    # Verificar error handling con stderr
    if "sys.stderr" not in content:
        warnings.append("WARNING: Se recomienda usar sys.stderr para mensajes de error")

    # Verificar try/except
    if "try:" not in content or "except" not in content:
        warnings.append("WARNING: Se recomienda try/except para manejar errores")

    # Verificar JSON parsing
    if "json.loads" not in content and "sys.stdin" in content:
        warnings.append("WARNING: Hook lee stdin pero no usa json.loads()")

    # Verificar que no usa subprocess con shell=True sin justificación
    if "shell=True" in content:
        warnings.append("WARNING: subprocess con shell=True puede ser inseguro")

    return errors, warnings


def validate_hooks_json(json_path):
    """Valida el archivo hooks.json"""
    errors = []
    warnings = []

    if not os.path.exists(json_path):
        return [f"ERROR: Archivo hooks.json no encontrado: {json_path}"], []

    # Validar JSON syntax
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return [f"ERROR: hooks.json tiene sintaxis JSON inválida: {e}"], []

    # Validar estructura
    if "hooks" not in config:
        errors.append("ERROR: hooks.json debe tener un campo 'hooks'")
        return errors, warnings

    hooks = config["hooks"]
    valid_events = [
        "SessionStart",
        "SessionEnd",
        "PreToolUse",
        "PostToolUse",
        "UserPromptSubmit",
        "Stop",
        "SubagentStop",
        "Notification",
        "PreCompact",
    ]

    for event, event_config in hooks.items():
        if event not in valid_events:
            warnings.append(f"WARNING: Tipo de evento desconocido: {event}")

        if not isinstance(event_config, list):
            errors.append(f"ERROR: '{event}' debe ser una lista")
            continue

        for hook_entry in event_config:
            if "hooks" not in hook_entry:
                errors.append(f"ERROR: Entrada en '{event}' debe tener campo 'hooks'")

            if "matcher" in hook_entry:
                matcher = hook_entry["matcher"]
                # Validar que matcher sea string
                if not isinstance(matcher, str):
                    errors.append(f"ERROR: 'matcher' debe ser string: {matcher}")

            for hook in hook_entry.get("hooks", []):
                if "type" not in hook:
                    errors.append(f"ERROR: Hook debe tener 'type'")
                elif hook["type"] != "command":
                    warnings.append(
                        f"WARNING: Tipo de hook no estándar: {hook['type']}"
                    )

                if "command" not in hook:
                    errors.append(f"ERROR: Hook de tipo 'command' debe tener 'command'")
                else:
                    cmd = hook["command"]
                    # Verificar que usa variable de entorno
                    if "${CLAUDE_PLUGIN_ROOT}" not in cmd and "~/" not in cmd:
                        warnings.append(
                            f"WARNING: Comando debería usar ${{CLAUDE_PLUGIN_ROOT}}: {cmd}"
                        )

                if "timeout" in hook:
                    timeout = hook["timeout"]
                    if not isinstance(timeout, (int, float)):
                        errors.append(f"ERROR: 'timeout' debe ser número: {timeout}")
                    elif timeout > 600:
                        warnings.append(
                            f"WARNING: Timeout muy alto: {timeout}s (max recomendado: 600s)"
                        )

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print(
            "Uso: validate_hook.py <ruta-al-hook.py> [ruta-a-hooks.json]",
            file=sys.stderr,
        )
        sys.exit(1)

    hook_file = sys.argv[1]
    hooks_json = sys.argv[2] if len(sys.argv) > 2 else "hooks/hooks.json"

    # Validar script
    errors, warnings = validate_hook_script(hook_file)

    # Validar hooks.json si existe
    if os.path.exists(hooks_json):
        json_errors, json_warnings = validate_hooks_json(hooks_json)
        errors.extend(json_errors)
        warnings.extend(json_warnings)
    else:
        warnings.append(f"WARNING: hooks.json no encontrado: {hooks_json}")

    # Reportar resultados
    if errors:
        print(f"\n❌ ERRORES:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print(f"\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors and not warnings:
        print(f"\n✅ Hook válido: {hook_file}")
        sys.exit(0)
    elif errors:
        sys.exit(1)  # Errores fatales
    else:
        sys.exit(0)  # Solo warnings, no fatal


if __name__ == "__main__":
    import re  # Necesario para validaciones de regex

    main()
