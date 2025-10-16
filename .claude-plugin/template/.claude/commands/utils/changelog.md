---
allowed-tools: Bash(git *, gh *, jq *)
description: Auto-detecta y actualiza CHANGELOG.md con PRs mergeados faltantes
---

# Changelog Update

Actualiza CHANGELOG.md con PRs mergeados siguiendo formato [Keep a Changelog](https://keepachangelog.com/), detecta tipos de commit y previene duplicados automáticamente.

## Uso

```bash
/changelog                               # Auto-detectar PRs faltantes (recomendado)
/changelog <pr_number>                   # Single PR
/changelog <pr1,pr2,pr3>                # Multiple PRs batch
```

## Ejemplos

```bash
/changelog                               # Auto-detecta todos los PRs faltantes
/changelog 130                           # Agregar PR #130
/changelog 128,129,130                  # Agregar múltiples PRs
```

## Ejecución

Cuando ejecutes este comando con el argumento `$ARGUMENTS`, sigue estos pasos:

### 1. Validación de herramientas

- Validar herramientas requeridas:
  - Ejecutar: `command -v gh >/dev/null 2>&1 || { echo "❌ Error: gh requerido"; exit 1; }`
  - Ejecutar: `command -v jq >/dev/null 2>&1 || { echo "❌ Error: jq requerido"; exit 1; }`
- Validar que CHANGELOG.md existe: `[[ -f CHANGELOG.md ]] || { echo "❌ Error: CHANGELOG.md no encontrado"; exit 1; }`

### 2. Auto-detección o parsing manual

**Si $ARGUMENTS está vacío (auto-detección):**

- Mostrar: "🔍 Auto-detectando PRs faltantes posteriores al último documentado..."
- Obtener último PR documentado: `last_pr=\`grep -oE 'PR #[0-9]+' CHANGELOG.md | grep -oE '[0-9]+' | sort -n | tail -1\``
- Validar que existe último PR: `test -n "$last_pr" || { echo "❌ Error: No se encontró PR previo en CHANGELOG"; exit 1; }`
- Mostrar último PR: `echo "📍 Último PR documentado: #$last_pr"`
- Obtener PRs mergeados desde git log: `git log --grep="Merge pull request" --pretty=format:"%s" --all | grep -oE "#[0-9]+" | tr -d '#' | sort -n -u > /tmp/git_prs.txt`
- Filtrar solo PRs mayores al último: `awk -v last="$last_pr" '$1 > last' /tmp/git_prs.txt > /tmp/new_prs.txt`
- Leer lista de PRs nuevos: `pr_list=\`cat /tmp/new_prs.txt | tr '\n' ' ' | sed 's/ $//'\``
- Limpiar archivos temporales: `rm -f /tmp/git_prs.txt /tmp/new_prs.txt`
- Verificar si hay PRs nuevos: `test -n "$pr_list" || { echo "✓ CHANGELOG está actualizado - no hay PRs nuevos posteriores a #$last_pr"; exit 0; }`
- Contar PRs encontrados: `new_count=\`echo "$pr_list" | wc -w\``
- Mostrar PRs a procesar: `echo "🔍 Encontrados $new_count PRs nuevos: $pr_list"`
- Mostrar inicio de procesamiento: `echo "Procesando PRs automáticamente..."`

**Si $ARGUMENTS tiene contenido (modo manual):**

- Convertir argumentos a lista (compatible zsh/bash): `pr_list=\`echo "$ARGUMENTS" | tr ',' ' '\``
- Validar que todos son números:
  - Para cada PR en la lista, ejecutar: `echo "$pr" | grep -qE '^[0-9]+$' || { echo "❌ Error: '$pr' no es número válido"; exit 1; }`
- Mostrar: "Procesando PR(s): $pr_list"

### 3. Validación de PRs en GitHub

Iterar sobre cada PR en `pr_list` ejecutando los siguientes comandos secuencialmente:

- Ejecutar: `pr_data=\`gh pr view "$pr" --json number,state,title,url 2>/dev/null\``
- Si comando falla o pr_data vacío:
  - Mostrar error: "❌ Error: PR #$pr no encontrado en GitHub"
  - TERMINAR proceso completamente
- Ejecutar: `pr_state=\`echo "$pr_data" | jq -r '.state'\``
- Si pr_state != "MERGED":
  - Mostrar error: "❌ Error: PR #$pr no está mergeado (estado: $pr_state)"
  - TERMINAR proceso completamente
- Ejecutar: `pr_title=\`echo "$pr_data" | jq -r '.title'\``
- Mostrar: "✓ PR #$pr validado: $pr_title"

### 4. Detección de duplicados en CHANGELOG

- Filtrar PRs duplicados verificando si cada PR ya existe en CHANGELOG.md
- Para PRs que ya existen, mostrar mensaje informativo y omitir
- Para PRs nuevos, mantener en lista para procesamiento
- Si no quedan PRs por procesar, mostrar mensaje y terminar exitosamente
- Mostrar lista final de PRs a agregar

### 5. Actualización de CHANGELOG (Keep a Changelog format)

Iterar sobre cada PR en `pr_list` ejecutando los siguientes pasos secuencialmente:

- Obtener datos completos: `pr_data=\`gh pr view "$pr" --json title,url --jq '{title, url}'\``
- Extraer título: `pr_title=\`echo "$pr_data" | jq -r '.title'\``
- Detectar sección por tipo de commit (feat: → Added, fix: → Fixed, otros → Changed)
- Obtener fecha actual para organización por fecha
- Actualizar CHANGELOG con orden correcto (más recientes primero):
  - Si fecha actual ya existe en CHANGELOG:
    - Si sección (Added/Fixed/Changed) existe en esa fecha: agregar entry después del header de sección
    - Si sección no existe: crear nueva sección en fecha existente
  - Si fecha actual no existe: crear nueva fecha al inicio con su sección correspondiente
- Mantener formato Keep a Changelog con entries como: `- título (PR #número)`
- Si sed falla, mostrar error: "❌ Error: Falló actualización para PR #$pr" y terminar

### 6. Validación post-actualización

- Validar que cada PR fue insertado correctamente en CHANGELOG.md
- Para cada PR procesado, verificar que el patrón "(PR #número)" existe usando: `grep -q "[(]PR #$pr[)]" CHANGELOG.md`
- Si algún PR no se encuentra, mostrar error específico y terminar proceso

### 7. Resultado final

- Mostrar: "✅ CHANGELOG.md actualizado exitosamente"
- Mostrar: "PRs agregados: ${pr_list[*]}"
- Mostrar cambios: `git diff --no-index /dev/null CHANGELOG.md | head -20`
- Mostrar: "💡 Recuerda hacer commit de los cambios: git add CHANGELOG.md && git commit -m 'docs: update CHANGELOG with PR(s) ${pr_list[*]}'"

**IMPORTANTE**:

- No solicitar confirmación al usuario en ningún paso
- Ejecutar todos los pasos secuencialmente con validaciones robustas
- Si algún paso crítico falla, restaurar estado y mostrar error claro
- Comando optimizado para actualizaciones batch y validación de integridad
- Detectar y prevenir duplicados automáticamente
