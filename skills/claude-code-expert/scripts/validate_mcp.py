#!/usr/bin/env python3
"""
Validador de configuración MCP para Claude Code
Valida sintaxis JSON y configuración de servidores MCP
Stdlib only - sin dependencias externas
"""

import sys
import os
import json
import re


def validate_mcp_json(file_path):
    """Valida un archivo .mcp.json"""
    errors = []
    warnings = []

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return [f"ERROR: Archivo no encontrado: {file_path}"], []

    # Validar JSON syntax
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return [f"ERROR: .mcp.json tiene sintaxis JSON inválida: {e}"], []

    # Validar estructura raíz
    if "mcpServers" not in config:
        errors.append("ERROR: .mcp.json debe tener un campo 'mcpServers'")
        return errors, warnings

    servers = config["mcpServers"]
    if not isinstance(servers, dict):
        errors.append("ERROR: 'mcpServers' debe ser un objeto")
        return errors, warnings

    # Validar cada servidor
    for server_name, server_config in servers.items():
        # Validar nombre de servidor
        if not re.match(r"^[a-z0-9-]+$", server_name):
            warnings.append(
                f"WARNING: Nombre de servidor '{server_name}' debería usar kebab-case"
            )

        if not isinstance(server_config, dict):
            errors.append(f"ERROR: Configuración de '{server_name}' debe ser un objeto")
            continue

        # Determinar tipo de transporte
        if "type" in server_config:
            transport_type = server_config["type"]

            if transport_type == "http":
                # Validar HTTP transport
                if "url" not in server_config:
                    errors.append(
                        f"ERROR: Servidor HTTP '{server_name}' debe tener 'url'"
                    )
                else:
                    url = server_config["url"]
                    # Verificar que sea URL válida o use expansión de env vars
                    if not url.startswith("http") and "${" not in url:
                        errors.append(
                            f"ERROR: URL inválida para '{server_name}': {url}"
                        )
                    # Recomendar HTTPS
                    if url.startswith("http://") and "${" not in url:
                        warnings.append(
                            f"WARNING: Se recomienda HTTPS en lugar de HTTP para '{server_name}'"
                        )

                # Validar headers si existen
                if "headers" in server_config:
                    headers = server_config["headers"]
                    if not isinstance(headers, dict):
                        errors.append(
                            f"ERROR: 'headers' de '{server_name}' debe ser un objeto"
                        )
                    else:
                        # Verificar que no haya credenciales hardcodeadas
                        for header_name, header_value in headers.items():
                            if isinstance(header_value, str):
                                if "${" not in header_value and len(header_value) > 20:
                                    # Podría ser un token hardcodeado
                                    if any(
                                        keyword in header_name.lower()
                                        for keyword in [
                                            "auth",
                                            "token",
                                            "key",
                                            "secret",
                                        ]
                                    ):
                                        warnings.append(
                                            f"WARNING: '{server_name}' podría tener credenciales hardcodeadas en headers"
                                        )

            elif transport_type == "sse":
                errors.append(
                    f"ERROR: Transport 'sse' está deprecated, usar 'http' para '{server_name}'"
                )

            elif transport_type not in ["http", "stdio"]:
                errors.append(
                    f"ERROR: Tipo de transporte desconocido '{transport_type}' para '{server_name}'"
                )

        elif "command" in server_config:
            # Stdio transport (legacy format without explicit type)
            command = server_config["command"]

            # Validar args
            if "args" in server_config:
                args = server_config["args"]
                if not isinstance(args, list):
                    errors.append(
                        f"ERROR: 'args' de '{server_name}' debe ser una lista"
                    )
                else:
                    # Verificar que no haya comandos peligrosos
                    for arg in args:
                        if not isinstance(arg, str):
                            warnings.append(
                                f"WARNING: Argumentos de '{server_name}' deberían ser strings"
                            )

            # Validar env
            if "env" in server_config:
                env = server_config["env"]
                if not isinstance(env, dict):
                    errors.append(f"ERROR: 'env' de '{server_name}' debe ser un objeto")
                else:
                    # Verificar que use expansión de variables
                    for env_name, env_value in env.items():
                        if isinstance(env_value, str):
                            if "${" not in env_value and len(env_value) > 20:
                                # Podría ser un secreto hardcodeado
                                if any(
                                    keyword in env_name.lower()
                                    for keyword in [
                                        "pass",
                                        "token",
                                        "key",
                                        "secret",
                                        "api",
                                    ]
                                ):
                                    warnings.append(
                                        f"WARNING: '{server_name}' podría tener secretos hardcodeados en env"
                                    )

        else:
            errors.append(
                f"ERROR: Servidor '{server_name}' debe tener 'type' o 'command'"
            )

    # Verificar que no esté vacío
    if not servers:
        warnings.append("WARNING: No hay servidores MCP configurados")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Uso: validate_mcp.py <ruta-a-.mcp.json>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    errors, warnings = validate_mcp_json(file_path)

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
