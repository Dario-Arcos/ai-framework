#!/usr/bin/env python3
"""
SessionEnd hook: Sync episodic-memory si está instalado

Comportamiento:
- Detecta si episodic-memory plugin está instalado
- Si existe: ejecuta sync en background (no bloquea)
- Si no existe: sale silenciosamente (exit 0)
- Nunca falla - el cierre de sesión no debe interrumpirse

Complementa el hook SessionStart del plugin episodic-memory:
- SessionStart (plugin): sync al INICIAR sesión (captura sesión anterior)
- SessionEnd (este hook): sync INMEDIATO al terminar (recomendado por docs)
"""
import os
import sys
import subprocess
from pathlib import Path


def find_episodic_memory_cli():
    """Busca el CLI de episodic-memory en ubicaciones conocidas

    Returns:
        Path | None: Ruta al CLI si existe y es ejecutable, None si no
    """
    # Ubicaciones conocidas del CLI
    candidates = [
        # Plugin instalado via superpowers-marketplace
        Path.home() / ".claude" / "plugins" / "cache" / "episodic-memory" / "cli" / "episodic-memory",
    ]

    for path in candidates:
        if path.exists() and os.access(path, os.X_OK):
            return path

    return None


def run_sync_background(cli_path):
    """Ejecuta episodic-memory sync en background

    Args:
        cli_path: Path al CLI de episodic-memory

    Returns:
        bool: True si se lanzó correctamente, False si falló
    """
    try:
        # Popen con start_new_session=True desacopla el proceso
        # stdout/stderr a DEVNULL para no bloquear
        subprocess.Popen(
            [str(cli_path), "sync", "--background"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            # No esperar - fire and forget
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def main():
    """Entry point del hook SessionEnd"""
    # Consumir stdin (Claude Code envía JSON con metadata)
    # Importante: si no leemos stdin, el pipe puede bloquearse
    try:
        sys.stdin.read()  # Consume y descarta
    except Exception:
        pass  # Ignorar errores de stdin

    # Buscar CLI de episodic-memory
    cli = find_episodic_memory_cli()

    if cli is None:
        # Plugin no instalado - salir silenciosamente
        # Esto es comportamiento esperado, no un error
        sys.exit(0)

    # Ejecutar sync en background (fire-and-forget)
    run_sync_background(cli)

    # Siempre exit 0 - nunca interrumpir cierre de sesión
    # El sync es best-effort, no crítico
    sys.exit(0)


if __name__ == "__main__":
    main()
