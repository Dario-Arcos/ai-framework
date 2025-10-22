---
description: Actualiza documentación basado en commits pendientes o análisis de inconsistencias
argument-hint: "[opcional: foco específico si no hay commits]"
allowed-tools: Bash(git *), Read, Edit, Grep, Glob, AskUserQuestion, TodoWrite
---

# Documentation Auto-Update

Actualiza documentación del proyecto mediante ingeniería inversa de commits pendientes o análisis proactivo de inconsistencias.

**Input:** `$ARGUMENTS` (opcional, usado solo en modo análisis enfocado)

## Flujo de Ejecución

### Paso 0: Determinar Modo de Operación

Ejecutar bash para detectar commits pendientes:

```bash
# Check for pending commits
commit_count=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")

if [ "$commit_count" -eq 0 ]; then
  echo "✅ No hay commits pendientes"
  echo "MODE=analysis"
else
  echo "📦 $commit_count commits pendientes detectados"
  echo "MODE=reverse_engineering"
fi

# Save mode for next steps
git config --local docs.update.mode "$MODE" 2>/dev/null || true
```

Según output, continuar con **FLUJO A** (reverse engineering) o **FLUJO B** (analysis).

---

## FLUJO A: Ingeniería Inversa (Commits Pendientes)

### A1. Analyze Pending Commits

Ejecutar bash para extraer información de commits:

```bash
# Get pending commits with file changes
git log origin/main..HEAD --oneline --name-status --no-merges > /tmp/pending_commits.txt

# Extract modified/renamed files
git diff --name-status origin/main..HEAD > /tmp/changed_files.txt

# Show summary
echo "=== Commits Analizados ==="
git log origin/main..HEAD --oneline --no-merges
echo ""
echo "=== Archivos Modificados ==="
cat /tmp/changed_files.txt
```

**Categorizar cambios:**

Claude debe analizar los archivos modificados y categorizarlos:

- Commands modificados: `commands/**/*.md`
- Agents modificados: `agents/**/*.md`
- Templates modificados: `.specify/templates/**`
- Config modificado: `*.md`, `.claude/**`

### A2. Identify Documentation Impact

Para cada archivo modificado en `commands/` o archivos renombrados, usar **ingeniería inversa**:

**Estrategia de búsqueda:**

1. **Para commands modificados:**
   - Extraer nombre del comando (ej: `cleanup.md` → `/cleanup`, `/ai-framework:git-github:cleanup`)
   - Buscar referencias en documentación:
     ```
     Grep pattern: "cleanup|/cleanup|git-github:cleanup"
     Path: docs/**/*.md
     Output: content con líneas
     ```

2. **Para archivos renombrados:**
   - Detectar pattern `R0XX old_path new_path` en git diff
   - Buscar referencias al path antiguo en docs
   - Buscar referencias al nombre antiguo del comando

3. **Para features añadidas:**
   - Leer commits para identificar nuevas features (keywords: "add", "implement", "feat:")
   - Buscar en docs secciones relacionadas que puedan necesitar actualización

**Crear mapa de impacto:**

Claude debe generar estructura mental como:

```
docs/commands-guide.md:
  - Línea 716: Referencia a /pr (renombrado a /pullrequest)
  - Línea 843: Descripción de /commit (añadido formato corporativo)
  - Línea 1933: Workflow table (contiene /pr)

docs/README.md:
  - Línea 45: Quick start menciona /pr
```

### A3. Generate Update Plan

Crear plan estructurado basado en mapa de impacto:

```markdown
## Plan de Actualización Documentación

### Cambios Detectados

**Commits analizados:**

- {commit_sha}: {commit_message}
- ...

**Archivos modificados relevantes:**

- {file_path} ({change_type})
- ...

### Impactos en Documentación

#### docs/commands-guide.md

- **Línea {num}**: {descripción_cambio_necesario}
  - Razón: {explicación_basada_en_commit}
  - Cambio propuesto: {old_text} → {new_text}

- **Línea {num}**: ...

#### docs/other-file.md

- ...

### Validaciones a Ejecutar

- [ ] VitePress build success
- [ ] No broken links introduced
- [ ] Markdown syntax valid

### Métricas Estimadas

- Archivos a modificar: {count}
- Líneas a cambiar: ~{estimate}
- Commits de referencia: {list}
```

Mostrar plan completo al usuario.

### A4. Request Authorization

Usar AskUserQuestion tool:

```
Pregunta: "¿Proceder con actualizaciones de documentación?"
Header: "Autorización"
Options:
  - label: "Sí, proceder"
    description: "Aplicar todas las actualizaciones planificadas"
  - label: "No, cancelar"
    description: "No modificar ningún archivo"
multiSelect: false
```

Si usuario selecciona "No" → exit con mensaje "Actualización cancelada por el usuario"

Si usuario selecciona "Sí" → continuar a A5

### A5. Execute Updates

Para cada cambio planificado:

1. **Read** archivo target
2. **Edit** con precisión quirúrgica (usar old_string y new_string exactos)
3. **TodoWrite** para tracking (opcional)
4. Mostrar progreso: "✓ Actualizado {file}:{line}"

**Después de todos los cambios:**

Validar si proyecto usa VitePress:

```bash
# Check if VitePress project
if [ -f "package.json" ] && grep -q "vitepress" package.json; then
  echo "Validating VitePress build..."
  npm run docs:build 2>&1 | tail -10

  if [ $? -ne 0 ]; then
    echo "❌ VitePress build failed - revisar cambios"
    exit 1
  else
    echo "✅ VitePress build passed"
  fi
fi
```

**Crear commit:**

```bash
# Generate commit message
git add docs/

# Create descriptive commit
git commit -m "docs: update documentation based on recent changes

Auto-generated by /update-docs command based on pending commits:
$(git log origin/main..HEAD --oneline --no-merges | head -5)

Changes:
- Updated command references
- Fixed outdated documentation
- Validated VitePress build

Files updated: $(git diff --cached --name-only | wc -l)"

echo "✅ Documentation updated and committed"
git log --oneline -n 1
```

**Mostrar summary:**

```
✅ Actualización Completada

Commits analizados: {count}
Archivos documentación actualizados: {count}
Líneas modificadas: +{additions} -{deletions}

Commit creado: {commit_sha}
VitePress build: ✅ PASSED

Estado: Listo para push
```

---

## FLUJO B: Análisis de Inconsistencias (Sin Commits Pendientes)

### B1. Request Analysis Mode

Usar AskUserQuestion tool:

```
Pregunta: "No hay commits pendientes. ¿Qué tipo de análisis de documentación quieres realizar?"
Header: "Modo Análisis"
Options:
  - label: "Análisis global"
    description: "Revisa toda la documentación buscando links rotos, referencias obsoletas y problemas de consistencia"
  - label: "Análisis enfocado"
    description: "Analiza un archivo o sección específica en detalle (usa $ARGUMENTS si proporcionado)"
  - label: "Cancelar"
    description: "No realizar ningún análisis"
multiSelect: false
```

Según respuesta:

- "Análisis global" → B2 modo GLOBAL
- "Análisis enfocado" → B2 modo FOCUSED
- "Cancelar" → exit con mensaje "Análisis cancelado"

### B2. Execute Analysis

**MODO GLOBAL:**

1. **Glob** todos los archivos de documentación:

   ```bash
   find docs -name "*.md" -type f 2>/dev/null || find . -name "*.md" -path "*/docs/*" -type f
   ```

2. Para cada archivo, **Read** y buscar:
   - **Links rotos:** Pattern `[text](path)` donde path no existe
   - **Comandos inexistentes:** Pattern `/command-name` o `/namespace:command` que no está en `commands/`
   - **Referencias a archivos movidos/eliminados**
   - **Versiones desactualizadas:** Comparar versiones mencionadas vs `package.json`

3. Validar comandos referenciados:

   ```bash
   # Get all available commands
   find commands -name "*.md" -type f | sed 's|commands/||; s|.md$||' > /tmp/available_commands.txt
   ```

   Para cada referencia de comando en docs, verificar si existe en lista.

**MODO FOCUSED:**

1. Determinar foco:
   - Si `$ARGUMENTS` proporcionado → usar como pattern (ej: "README", "commands-guide", "\*.md")
   - Si no → preguntar al usuario con AskUserQuestion

2. **Glob** o **Read** archivos específicos según foco

3. Análisis profundo:
   - Todas las validaciones del modo GLOBAL
   - Plus: referencias salientes (links a otros docs)
   - Plus: consistencia con archivos relacionados

**Output de análisis (ambos modos):**

Generar reporte estructurado:

```markdown
## Análisis de Inconsistencias

### Archivos Analizados: {count}

### Problemas Detectados

#### Links Rotos ({count})

**docs/commands-guide.md:**

- Línea 234: `[Agent Guide](/agents/old-agent.md)` → archivo no existe
- Línea 567: `[Setup](../setup.md)` → path incorrecto

**docs/README.md:**

- Línea 89: `[Contributing](CONTRIBUTING.md)` → archivo faltante

#### Comandos Inexistentes ({count})

**docs/commands-guide.md:**

- Línea 456: Referencia `/ai-framework:old-command` → no existe en commands/
- Línea 789: Referencia `/deprecated` → comando eliminado

#### Versiones Desactualizadas ({count})

**docs/README.md:**

- Línea 12: Menciona "v1.2.0" → package.json actual: "v1.3.1"

### Inconsistencias Cross-Document ({count})

- `commands-guide.md` menciona feature X, pero `README.md` no
- Discrepancia en nombre de comando entre archivos

### Summary

- Total problemas: {count}
- Críticos: {count} (links rotos, comandos inexistentes)
- Advertencias: {count} (versiones, inconsistencias)
```

### B3. Generate Correction Plan

Similar a A3, crear plan estructurado con correcciones propuestas:

```markdown
## Plan de Corrección

### docs/commands-guide.md

- **Línea 234**: Corregir link roto
  - Actual: `[Agent Guide](/agents/old-agent.md)`
  - Propuesto: `[Agent Guide](/agents/current-agent.md)` o eliminar link

- **Línea 456**: Actualizar comando obsoleto
  - Actual: `/ai-framework:old-command`
  - Propuesto: `/ai-framework:new-command` o actualizar a sintaxis correcta

### docs/README.md

- **Línea 12**: Actualizar versión
  - Actual: "v1.2.0"
  - Propuesto: "v1.3.1" (desde package.json)

### Validaciones

- [ ] VitePress build
- [ ] All links valid
- [ ] Command references exist
```

Mostrar plan al usuario.

### B4. Request Authorization

Usar AskUserQuestion tool (igual que A4):

```
Pregunta: "¿Proceder con correcciones propuestas?"
Header: "Autorización"
Options:
  - label: "Sí, aplicar correcciones"
    description: "Modificar archivos según el plan"
  - label: "No, cancelar"
    description: "No realizar cambios"
multiSelect: false
```

Si "No" → exit
Si "Sí" → continuar a B5

### B5. Execute Corrections

Exactamente igual que A5:

1. Para cada corrección planificada → **Read** + **Edit** quirúrgico
2. Validar VitePress build si aplica
3. Crear commit descriptivo
4. Mostrar summary

```bash
git commit -m "docs: fix inconsistencies found by analysis

Auto-generated by /update-docs command (analysis mode)

Corrections applied:
- Fixed {count} broken links
- Updated {count} command references
- Corrected version numbers
- Resolved cross-document inconsistencies

Analysis type: {global|focused}
Files corrected: $(git diff --cached --name-only | wc -l)"
```

---

## Error Handling

**Sin commits y modo cancelado:**

```
ℹ️ No hay commits pendientes y análisis cancelado
No se realizaron cambios
```

**Todos los cambios ya aplicados:**

```
✅ Documentación ya está actualizada
No se detectaron cambios necesarios
```

**VitePress build falla:**

```
❌ Error: VitePress build failed

Los cambios no fueron committeados.
Revisa los errores arriba y ejecuta manualmente:
  npm run docs:build

Para revertir cambios:
  git restore docs/
```

**Usuario rechaza autorización:**

```
ℹ️ Actualización cancelada por el usuario
No se realizaron cambios en la documentación
```

---

## Notas de Implementación

**Template-Driven Approach:**

- Todas las instrucciones son procesadas por Claude naturalmente
- No bash scripts complejos (solo git commands atómicos)
- Pattern matching y análisis vía capacidades de Claude
- Edits quirúrgicos con old_string/new_string exactos

**Autorización Explícita:**

- NUNCA modificar archivos sin autorización del usuario
- Siempre mostrar plan completo antes de cambios
- Usuario controla el flujo en todo momento

**Validaciones:**

- VitePress build si proyecto lo usa
- Git status clean antes de commit
- Links validation cuando sea posible

**Commits Descriptivos:**

- Auto-generated con contexto completo
- Referencias a commits originales (Flujo A)
- Lista de cambios aplicados
- Métricas incluidas
