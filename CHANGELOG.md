# Historial de Cambios

Todos los cambios importantes de AI Framework se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [No Publicado]

### Añadido

- Mejoras de CI/CD: Workflow de GitHub Pages ahora se dispara automáticamente con cambios en CHANGELOG.md

### Cambiado

- Plugin structure: hooks/ y template/ movidos a plugin root per especificación oficial (PR #15)
- Plugin configuration: eliminada redundancia en marketplace.json, versión sincronizada (PR #15)
- Command workflow: pr.md ahora crea branch temporal ANTES de pre-review (permite correcciones) (PR #14, #15)
- Template naming: archivos framework usan sufijo .template para instalación (PR #14)

### Arreglado

- Security: command injection risk en pr.md (sanitización de pr_title, uso de --body-file) (PR #15)
- Reliability: persistencia de variables en pr.md usando git config (corrige fatal error) (PR #15)
- Configuration: hooks.json formato estándar (sin matchers innecesarios en UserPromptSubmit/Stop/Notification) (PR #15)
- Configuration: eliminados timeouts redundantes de hooks (usa default 60s) (PR #15)
- Gitignore: rutas actualizadas para nueva estructura (/hooks/ en lugar de /.claude-plugin/hooks/) (PR #15)
- Complexity: simplificación de commands (pr.md, changelog.md, cleanup.md, commit.md) (PR #14)
- Documentation: resolución de errors de parser Vue en VitePress (PR #13)
- Plugin: unificación de agents/commands a patrón template-based (PR #12)
- Documentation: refinamiento de workflow y eliminación de agent-assignment obligatorio (PR #10, #11)
- Documentation: mejoras de calidad y gestión de versiones (PR #9)

---

## [1.1.1] - 2025-10-16

### Añadido

**Gestión Automática de Versiones**

Ahora puedes actualizar la versión del framework en todos los archivos con un solo comando:

- Ejecuta `npm version patch` (o `minor`/`major`) y automáticamente se sincronizan: package.json, documentación VitePress, README, y badges visuales
- Nuevo componente de comparación de versiones en la documentación (muestra versión actual vs anterior)
- Validación automática: el script verifica que exista entrada en CHANGELOG antes de crear la versión
- Documentación del flujo completo en README → sección "Version Management"

**Comandos Opcionales para Optimizar tu Workflow**

Tres nuevos comandos opcionales con guía de cuándo usarlos:

- `/analyze`: Análisis de consistencia entre spec, plan y tasks (ejecutar después de generar tasks)
- `/checklist`: Genera lista de verificación PRE-implementación basada en tus requerimientos
- `/sync`: Publica tu especificación como issue en GitHub vinculado al PRP padre (POST-implementación)
- **Modo consulta**: Usa `agent-strategy-advisor` para obtener recomendaciones de agentes antes de ejecutar

### Cambiado

**⚠️ Cambio Importante: Sincronización Automática de Agentes y Comandos**

Los agentes y comandos del framework ahora se actualizan automáticamente desde templates centralizados:

- **Qué significa para ti**: Recibirás actualizaciones de agentes/comandos sin perder tus configuraciones personalizadas
- **Acción requerida**: Después de actualizar el plugin, reinicia Claude Code para cargar los cambios
- **Breaking change**: Si personalizaste archivos en `.claude/agents/` o `.claude/commands/`, respáldalos antes de actualizar

**Mejoras Generales del Framework**

Actualizaciones críticas de estabilidad y correcciones varias que mejoran la experiencia general del framework.

**Workflow SDD Simplificado (6 Pasos)**

El workflow principal se redujo de 7 a 6 pasos:

- **Eliminado**: Paso obligatorio de "Agent Assignment" (análisis demostró ROI negativo)
- **Transformado**: `agent-assignment-analyzer` → `agent-strategy-advisor` (ahora consultivo, no automático)
- **Reposicionado**: Checklist ahora es PRE-implementación (valida especificaciones, no código)
- **Clarificado**: Comando `/sync` es opcional, para documentación POST-implementación en GitHub

**Resultado**: Menos fricción, mayor flexibilidad, mismo nivel de calidad.

### Eliminado

**Simplificación Visual de la Documentación**

Eliminamos elementos redundantes para mejorar la claridad:

- Badge de release duplicado en homepage (ahora integrado en componente VersionBadge)
- Emojis decorativos en docs (conservados solo funcionales: ✅❌⚠️➜)
- Links rotos en tarjetas de features
- Referencias hardcodeadas a números de componentes (ahora enlaces autoritativos)

**Reducción de Complejidad en Workflow**

- 63 líneas de documentación obsoleta sobre "Agent Assignment"
- 11 instancias de spanglish en documentación (PRE-/POST-, cross-, multi-)
- Referencias obsoletas a `agent-assignment-analyzer` en tablas y tips

### Arreglado

**Documentación VitePress**

- Resueltos errores de parsing de Vue causados por sintaxis de placeholders
- Corregidos problemas de compatibilidad que impedían build de documentación
- Documentación ahora compila sin warnings

**Precisión en Documentación del Workflow**

- Clarificado propósito de checklist: "tests unitarios de la especificación" (no tests de implementación)
- Mejorada separación español/inglés (terminología profesional consistente)
- Corregida numeración de pasos del workflow en todos los archivos
- Corregido cálculo de complejidad constitucional (clasificación L-size, no M-size)

---

## [1.1.0] - 2025-10-15

### Añadido

**Sistema de Diseño Monocromático Premium** (PR #8)

- Rediseño completo del sitio de documentación con estética brutalista inspirada en Apple
- Tema monocromático con gradiente (Negro #18181B → Carbón #52525B)
- Animaciones premium en botones: escala al hover + efecto shine con easing estándar de Apple
- Nuevos íconos de activos: `terminal.svg` (Comandos), `zap.svg` (Pro Tips) desde librería Lucide
- Grid de features balanceado 4-tarjetas (layout 2x2) reemplazando diseño 5-tarjetas desbalanceado

### Cambiado

**Sistema de Diseño Visual** (PR #8)

- Sección hero: Eliminado campo de nombre redundante para enfoque minimalista
- Jerarquía de botones: Workflow como botón primario de marca, Quick Start/Changelog como secundarios
- Color de marca: Cambiado de azul GitHub (#0969da) a monocromático (#18181b)
- Badge de release: Actualizado a color monocromático para consistencia visual
- Tipografía: Mejorada con font-weight 800, letter-spacing ajustado (-0.5px) para autoridad
- Modo oscuro: Optimizado con gradientes invertidos (espectro Blanco→Gris)

**Mejoras en Documentación** (PR #8)

- Estructura de navegación mejorada en todas las páginas de documentación
- Claridad y legibilidad de contenido mejoradas
- Homepage reorganizada para enfatizar propuesta de valor: "Desarrollo con IA que funciona"

### Seguridad

**Revisión de Seguridad de Diseño** (PR #8)

- Aprobada revisión de seguridad con score de confianza 0.95
- Sin credenciales hardcodeadas o secretos detectados
- Activos SVG verificados como seguros (sin scripts o event handlers)
- Guía apropiada de gestión de secretos mantenida en documentación MCP

---

## [1.0.0] - 2025-10-15

### Añadido

**Documentación Human Handbook** (GitHub Pages)

- Documentación completa de workflow para ecosistema PRP → SDD → GitHub
- 6 guías completas: Quickstart, AI-First Workflow, Commands Guide, Agents Guide, Pro Tips, MCP Servers
- Matriz de decisión Branch vs Worktree con 4 escenarios de uso
- Paso agent-assignment-analyzer en workflow (SDD-cycle paso 5) con ejemplos de ejecución paralela
- Diagramas de workflow (Mermaid) para ciclo completo de desarrollo
- Referencias cruzadas entre todos los archivos de documentación

**Componentes del Framework**

- 7 lifecycle hooks (Python): session-start, workspace-status, pre-tool-use, security_guard, clean_code, minimal_thinking, ccnotify
- 24 slash commands en 4 categorías: PRP-cycle (2), SDD-cycle (9), git-github (5), utils (8)
- 45 agentes especializados en 11 categorías
- Framework de gobernanza constitucional con 5 principios no negociables
- Workflow de Specification-Driven Development (SDD) con trazabilidad de artefactos

### Cambiado

**Sintaxis de Comandos**

- Actualizadas todas las referencias de comandos para usar namespace completo del plugin (`/ai-framework:category:command`)
- Corregida terminología PRP-cycle (anteriormente PRD-cycle) en toda la documentación
- Actualizado conteo de comandos de 22 a 24 comandos en todos los docs

**Workflow SDD-Cycle**

- Documentado orden correcto de ejecución (9 pasos): specify → clarify → plan → tasks → **agent-assignment** → analyze → implement → checklist → sync
- Agregado agent-assignment-analyzer como paso 5 (CRÍTICO - casi mandatorio) para optimización de ejecución paralela
- Movido checklist a paso 8 (validación de calidad POST-implementación)
- Clarificado que analyze y sync son opcionales pero recomendados

### Arreglado

**Documentación de Comportamiento Funcional**

- Corregido comportamiento de `speckit.specify`: crea branch en MISMO directorio (NO crea worktree)
- Corregido comportamiento de `speckit.specify`: NO abre IDE automáticamente
- Clarificado que `worktree:create` es el ÚNICO comando que crea worktrees aislados
- Corregidos ejemplos de workflow para mostrar comportamiento correcto de comandos
- Agregadas advertencias explícitas sobre diferencias branch vs worktree

**Precisión en Documentación**

- Corregidos 7 workflows con secuencias correctas de comandos
- Corregidas 191 referencias de sintaxis de comandos en 4 archivos
- Actualizadas todas las fechas a 2025-10-14
- Corregidas referencias de conteo de agentes (45 agentes, no 44)

### Seguridad

**Seguridad Preventiva**

- Arquitectura security-first con hook PreToolUse `security_guard.py`
- 5 patrones críticos bloqueados: credenciales hardcodeadas, inyección eval, inyección SQL, inyección de comandos, path traversal
- Revisión de seguridad BLOQUEANTE en workflow de creación de PR

---

**Estado de Producción**: ✅ LISTO PARA RELEASE

Este release representa el AI Framework completo y listo para producción con:

- Instalación automática sin configuración
- Aplicación de gobernanza constitucional
- 45 agentes especializados
- Documentación completa validada contra código fuente
- Todos los workflows probados y ejecutables

**Breaking Changes**: Ninguno (release inicial)

**Guía de Migración**: No aplica (release inicial)

---

## Formato de Notas de Release

Al publicar un release, la sección `[No Publicado]` será reemplazada con:

```
## [X.Y.Z] - YYYY-MM-DD

### Añadido
- Nuevas funcionalidades

### Cambiado
- Cambios en funcionalidad existente

### Obsoleto
- Funcionalidades que pronto serán eliminadas

### Eliminado
- Funcionalidades eliminadas

### Arreglado
- Correcciones de errores

### Seguridad
- Correcciones de vulnerabilidades de seguridad
```

---

**Leyenda:**

- **Major (X.0.0):** Breaking changes, nuevas funcionalidades mayores
- **Minor (x.Y.0):** Nuevas funcionalidades compatibles hacia atrás
- **Patch (x.y.Z):** Correcciones de errores compatibles hacia atrás
