# Guía de Expert Skills

::: tip Navegación Rápida
Skills son capacidades especializadas que se activan automáticamente según el contexto de tu solicitud. No requieren invocación explícita.
:::

---

| Skill                                     | Dominio                 | Activación                                   |
| ----------------------------------------- | ----------------------- | -------------------------------------------- |
| [claude-code-expert](#claude-code-expert) | Claude Code Development | Crear/modificar agents, commands, hooks, MCP |
| [algorithmic-art](#algorithmic-art)       | Generative Art          | Arte algorítmico, p5.js, flow fields         |
| [skill-creator](#skill-creator)           | Skill Development       | Crear/actualizar skills                      |

---

## claude-code-expert

Genera componentes Claude Code (agents, commands, hooks, MCP) correctos en primer intento siguiendo documentación oficial y patrones ai-framework.

**Cuándo usarla:**

- "Crea un agente para X"
- "Agrega un comando para X"
- "Implementa un hook para X"
- "Integra X vía MCP"

**Cómo funciona:**

1. WebFetch docs oficiales (sintaxis actual)
2. Analiza patrones existentes del proyecto
3. Genera componente fusionando oficial + proyecto + constitución
4. Valida automáticamente (syntax + security + logic)

**Output:** Componente production-ready validado con 6 quality gates (syntax, security, logic, constitutional, integration, production-ready).

**Detalles completos:** `skills/claude-code-expert/SKILL.md`

---

## algorithmic-art

Crea arte generativo p5.js con filosofías algorítmicas originales. Produce viewers interactivos con seed navigation y controles paramétricos.

**Cuándo usarla:**

- "Arte generativo de X"
- "Flow fields con partículas"
- "Arte algorítmico inspirado en Y"

**Cómo funciona:**

1. Crea filosofía algorítmica (movimiento estético computacional)
2. Implementa algoritmo p5.js expresando la filosofía
3. Genera viewer interactivo con Anthropic branding

**Output:** Filosofía (.md) + HTML interactivo con seed navigation, controles paramétricos, y reproducibilidad (mismo seed = mismo output).

**Detalles completos:** `skills/algorithmic-art/SKILL.md`

---

## skill-creator

Meta-skill que guía creación de nuevas skills efectivas mediante proceso estructurado en 6 pasos.

**Cuándo usarla:**

- "Crea una skill para X"
- "Necesito extender capacidades con Y"

**Cómo funciona:**

1. Valida casos de uso concretos
2. Identifica recursos necesarios (scripts/references/assets)
3. Genera estructura con `init_skill.py`
4. Guía edición de SKILL.md
5. Valida y empaqueta con `package_skill.py`

**Output:** Skill empaquetada (.zip) lista para distribución con validación automática pasada.

**Detalles completos:** `skills/skill-creator/SKILL.md`

---

## Uso de Skills

Las skills se activan automáticamente cuando tu solicitud coincide con su dominio. Para crear nuevas skills, simplemente pide: _"Crea una skill para [dominio]"_ y `skill-creator` guiará el proceso.

**Recursos:** `scripts/init_skill.py` | `scripts/package_skill.py`
