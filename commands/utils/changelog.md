---
allowed-tools: Bash(git *, gh *), Read, Edit
description: Actualiza CHANGELOG.md usando template Keep a Changelog en español
argument-hint: "todos los PRs" | "PR #123" | "desde v1.2.0"
---

# Actualización de CHANGELOG

Actualiza la sección `[No Publicado]` del CHANGELOG.md con información de PRs.

**Input**: `$ARGUMENTS` - Descripción natural de qué actualizar

## Ejemplos de Uso

```bash
/ai-framework:utils:changelog "todos los PRs desde última versión"
/ai-framework:utils:changelog "PR #123 y #124"
/ai-framework:utils:changelog "desde v1.2.0"
/ai-framework:utils:changelog "últimos 5 PRs mergeados"
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

- Descripción clara y específica del cambio (PR #123)
```

## Workflow de Ejecución

### 1. Interpretar Argumentos

**Responsabilidad de Claude**: Parsear `$ARGUMENTS` para determinar:

- ¿Qué PRs actualizar? (todos, específicos, rango)
- ¿Desde dónde? (último tag, versión específica, HEAD)

**Ejemplos**:

- "todos los PRs" → Desde último git tag hasta HEAD
- "PR #123" → Solo ese PR específico
- "desde v1.2.0" → Desde tag v1.2.0 hasta HEAD
- "últimos 5 PRs" → 5 PRs mergeados más recientes

### 2. Obtener PRs

Ejecutar bash según interpretación:

```bash
# Opción A: Desde último tag
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
pr_list=$(git log "$last_tag..HEAD" --oneline | grep -oE '#[0-9]+' | tr -d '#' | sort -u)

# Opción B: PRs específicos
pr_list="123 124"

# Opción C: Últimos N PRs
pr_list=$(git log --oneline | grep -oE '#[0-9]+' | tr -d '#' | head -5 | sort -u)
```

### 3. Procesar Cada PR

Para cada PR en `$pr_list`:

```bash
# Obtener metadata
pr_data=$(gh pr view "$pr_num" --json title,body,state)
```

**Responsabilidad de Claude**:

1. **Extraer título y body** del JSON
2. **Verificar estado** MERGED (skip si no)
3. **Determinar categoría Keep a Changelog**:
   - `feat:` → **Añadido**
   - `fix:` → **Arreglado**
   - `docs:` → (skip o categoría específica según contexto)
   - `refactor:`, `perf:` → **Cambiado**
   - `security:` → **Seguridad**
   - Otros → Preguntar al usuario o usar **Cambiado**

4. **Construir descripción en español**:
   - Si body tiene contenido útil: usar resumen del body
   - Si body vacío: limpiar título (quitar `feat:`, scope)
   - Traducir al español si está en inglés
   - Ser específico: QUÉ cambió, no "cambios en X archivos"

5. **Agrupar por categoría**

### 4. Actualizar CHANGELOG.md

**Responsabilidad de Claude**:

1. Leer CHANGELOG.md completo
2. Localizar sección `## [No Publicado]`
3. Construir contenido nuevo con categorías ordenadas:

   ```markdown
   ## [No Publicado]

   ### Añadido

   - Descripción específica feature 1 (PR #123)
   - Descripción específica feature 2 (PR #124)

   ### Arreglado

   - Descripción específica fix 1 (PR #125)
   ```

4. Usar Edit tool para reemplazar sección completa
5. Verificar con Read tool

### 5. Reportar Resultado

Mostrar resumen al usuario:

```
✅ CHANGELOG actualizado

Categorías modificadas:
- Añadido: 2 entradas
- Arreglado: 1 entrada

PRs procesados: #123, #124, #125
```

## Principios de Diseño

**Simplicidad**:

- Claude decide implementación (no bash scripts complejos)
- Zero git config state management
- Zero retry logic explícito (gh CLI es confiable)

**Claridad**:

- Descripciones en español, específicas
- Template Keep a Changelog estricto
- Usuario controla qué actualizar vía lenguaje natural

**Flexibilidad**:

- Argumentos en lenguaje natural
- Claude interpreta intención
- Adaptable a diferentes workflows

## Notas

- **Idioma**: Todas las entradas en español
- **Especificidad**: Describir QUÉ cambió, no "cambios en N archivos"
- **Breaking changes**: Destacar con ⚠️ **BREAKING**
- **No commit automático**: Usuario decide cuándo commitear
