---
allowed-tools: Bash(git *, gh *), Read, Edit
description: Actualiza CHANGELOG.md analizando commits de PRs con detalle técnico
argument-hint: "todos los PRs" | "PR #123" | "desde v1.2.0"
---

# Actualización de CHANGELOG

Actualiza la sección `[No Publicado]` del CHANGELOG.md con análisis detallado de commits y archivos modificados por cada PR.

**Input**: `$ARGUMENTS` - Descripción natural de qué actualizar

## Ejemplos de Uso

```bash
/ai-framework:utils:changelog "todos los PRs desde última versión"
/ai-framework:utils:changelog "PR #23"
/ai-framework:utils:changelog "desde v2.0.0"
/ai-framework:utils:changelog "últimos 3 PRs mergeados"
```

## Template Keep a Changelog (Español)

**Categorías** (en orden):

1. **Añadido** - Nuevas funcionalidades
2. **Cambiado** - Cambios en funcionalidad existente
3. **Obsoleto** - Funcionalidades que serán eliminadas
4. **Eliminado** - Funcionalidades eliminadas
5. **Arreglado** - Corrección de bugs
6. **Seguridad** - Vulnerabilidades corregidas

**Formato de entrada**:

```markdown
### [Categoría]

- Descripción técnica y específica del cambio (PR #123)
```

## Workflow de Ejecución

### 1. Interpretar Argumentos

**Responsabilidad de Claude**: Parsear `$ARGUMENTS` para determinar:

- ¿Qué PRs actualizar? (todos, específicos, rango)
- ¿Desde dónde? (último tag, versión específica, HEAD)

**Ejemplos**:

- "todos los PRs" → Desde último git tag hasta HEAD
- "PR #123" → Solo ese PR específico
- "desde v2.0.0" → Desde tag v2.0.0 hasta HEAD
- "últimos 3 PRs" → 3 PRs mergeados más recientes

### 2. Obtener PRs

Ejecutar bash según interpretación:

```bash
# Opción A: Desde último tag
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
pr_list=$(git log "$last_tag..HEAD" --oneline | grep -oE '#[0-9]+' | tr -d '#' | sort -u)

# Opción B: PRs específicos
pr_list="123"

# Opción C: Últimos N PRs
pr_list=$(git log --oneline | grep -oE '#[0-9]+' | tr -d '#' | head -3 | sort -u)
```

### 3. Analizar Cada PR en Profundidad

Para cada PR en `$pr_list`:

```bash
# Metadata básica del PR
pr_data=$(gh pr view "$pr_num" --json title,state,mergedAt,body)

# CRÍTICO: Obtener commits individuales del PR
pr_commits=$(gh pr view "$pr_num" --json commits --jq '.commits[] | "\(.messageHeadline)|\(.oid[:7])"')

# CRÍTICO: Obtener archivos modificados para contexto técnico
pr_files=$(gh pr view "$pr_num" --json files --jq '.files[].path')
```

**Responsabilidad de Claude**:

1. **Verificar estado** MERGED (skip si no mergeado)

2. **Analizar commits individuales** (no solo título del PR):
   - Extraer mensajes de commit
   - Identificar patrones técnicos (feat/fix/refactor/etc.)
   - Entender secuencia de cambios

3. **Analizar archivos modificados**:
   - Identificar módulos/componentes afectados
   - Detectar alcance técnico (frontend/backend/config/docs)
   - Extraer contexto para descripción precisa

4. **Determinar categoría Keep a Changelog**:
   - `feat:` → **Añadido**
   - `fix:` → **Arreglado**
   - `docs:` → (skip o **Cambiado** si sustancial)
   - `refactor:`, `perf:` → **Cambiado**
   - `security:` → **Seguridad**
   - `chore:` → (evaluar contexto)
   - Otros → **Cambiado** (por defecto)

5. **Construir descripción técnica en español**:
   - **Basada en commits + archivos**, no solo título PR
   - **QUÉ cambió técnicamente** (no "cambios en X archivos")
   - **Específica**: módulos, funcionalidades, impacto
   - **Concisa**: 1-2 líneas, sin verbosidad innecesaria
   - **Traducir** al español si está en inglés
   - **Breaking changes**: marcar con ⚠️ **BREAKING** si detectado

6. **Agrupar por categoría**

### 4. Actualizar CHANGELOG.md

**Responsabilidad de Claude**:

1. Leer CHANGELOG.md completo
2. Localizar sección `## [No Publicado]`
3. Construir contenido nuevo con categorías ordenadas:

   ```markdown
   ## [No Publicado]

   ### Añadido

   - Descripción técnica específica feature 1 basada en commits/archivos (PR #123)
   - Descripción técnica específica feature 2 (PR #124)

   ### Cambiado

   - ⚠️ **BREAKING**: Descripción del breaking change con contexto técnico (PR #125)

   ### Arreglado

   - Descripción específica del fix con módulos afectados (PR #126)
   ```

4. Usar Edit tool para reemplazar sección completa
5. Verificar con Read tool

### 5. Reportar Resultado

Mostrar resumen al usuario:

```
✅ CHANGELOG actualizado

Categorías modificadas:
- Añadido: 2 entradas
- Cambiado: 1 entrada (1 breaking change)
- Arreglado: 1 entrada

PRs procesados: #123, #124, #125, #126
Commits analizados: 12
Archivos analizados: 8
```

## Reglas

- **Analizar commits + archivos** para entender QUÉ cambió técnicamente
- **Entradas en español**, específicas y técnicas (no genéricas)
- **Breaking changes** con ⚠️ **BREAKING**
- **NO commitear automáticamente** (usuario decide cuándo)
- **Concisión con precisión**: 1-2 líneas por entrada, máximo detalle técnico
