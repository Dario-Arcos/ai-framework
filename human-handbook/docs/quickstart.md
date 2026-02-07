# Inicio rápido

Instala el framework y empieza a usarlo.

---

## Instalación

::: code-group
```bash [Primera vez]
# Agregar marketplace
/plugin marketplace add Dario-Arcos/ai-framework-marketplace

# Instalar plugin
/plugin install ai-framework@ai-framework-marketplace
```

```bash [Actualizar]
# Sincronizar marketplace (necesario, no se hace automático)
/plugin marketplace update ai-framework-marketplace

# Actualizar plugin
/plugin update ai-framework@ai-framework-marketplace
```

```bash [Reinstalar limpio]
/plugin marketplace remove ai-framework-marketplace
/plugin marketplace add Dario-Arcos/ai-framework-marketplace
/plugin install ai-framework@ai-framework-marketplace
```
:::

Reinicia Claude Code después de instalar o actualizar.

---

## Inicializar proyecto

```bash
cd /tu/proyecto
claude
```

En la primera sesión, ejecuta:

```bash
/project-init
```

Genera reglas en `docs/claude-rules/` (para compartir con el equipo) y las sincroniza a `.claude/rules/` (copia local).

::: details Gestión de plugins
```bash
# Deshabilitar temporalmente
/plugin disable ai-framework@ai-framework-marketplace

# Re-habilitar
/plugin enable ai-framework@ai-framework-marketplace

# Desinstalar
/plugin uninstall ai-framework@ai-framework-marketplace

# Explorar plugins disponibles
/plugin
```
Reinicia después de cualquier cambio.
:::

---

## Usar el framework

Describe lo que quieres en lenguaje natural:

```
"Implementa validación de email en el formulario de registro"
```

Claude activa automáticamente los skills relevantes (TDD, code review, etc).

Para commits y PRs:

```bash
/git-commit "feat: add email validation"
/pull-request develop
```

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Comandos no visibles | Reinicia Claude Code |
| Hooks no ejecutan | Verifica Python 3.8+: `python3 --version` |
| Plugin no aparece | `/plugin` y busca en el marketplace |
| Update no funciona | Ejecuta primero `/plugin marketplace update` |

---

## Requisitos

- [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation)
- [Git](https://git-scm.com/downloads)
- [Python 3.8+](https://www.python.org/downloads/)
- [GitHub CLI](https://cli.github.com/) (opcional, para comandos git)

---

## Siguientes pasos

- [Commands Guide](./commands-guide.md) — Comandos disponibles
- [Agents Guide](./agents-guide.md) — Agentes especializados
- [Skills Guide](./skills-guide.md) — Skills del framework
- [Integrations](./integrations.md) — Plugins y MCPs externos

---

::: info Última actualización
**Fecha**: 2026-01-31
:::
