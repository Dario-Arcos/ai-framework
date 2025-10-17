---
allowed-tools: Bash(git *, gh *, jq *, npm version *)
description: Actualiza CHANGELOG.md con PRs mergeados en formato español Keep a Changelog
---

# Changelog Update (Español)

Actualiza CHANGELOG.md con PRs mergeados siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) en español. Detecta tipos de commit, previene duplicados y opcionalmente ejecuta release automático.

## Uso

```bash
/changelog                     # Auto-detectar PRs → insertar en [No Publicado]
/changelog 130                 # Single PR → insertar en [No Publicado]
/changelog 128,129,130         # Multiple PRs → insertar en [No Publicado]
/changelog patch               # Auto-detectar + release patch automático
/changelog 130,131 minor       # PRs específicos + release minor automático
```

## Ejemplos

```bash
# Uso común: agregar PRs sin hacer release
/changelog                     # Detecta automáticamente PRs faltantes

# Release completo en un comando
/changelog patch               # Agregar PRs + release patch (1.1.1 → 1.1.2)
/changelog minor               # Agregar PRs + release minor (1.1.1 → 1.2.0)
```

## Ejecución

Cuando ejecutes este comando con el argumento `$ARGUMENTS`, sigue estos pasos:

### 1. Validación de herramientas

```bash
command -v gh >/dev/null 2>&1 || {
  echo "❌ Error: gh CLI requerido"
  echo "💡 Instalar: https://cli.github.com/"
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "❌ Error: jq requerido"
  echo "💡 Instalar: brew install jq (macOS) o apt install jq (Ubuntu)"
  exit 1
}
[[ -f CHANGELOG.md ]] || {
  echo "❌ Error: CHANGELOG.md no encontrado en $(pwd)"
  echo "💡 Asegúrate de estar en la raíz del proyecto"
  exit 1
}

# Validar que existe sección [No Publicado]
grep -q "^## \[No Publicado\]" CHANGELOG.md || {
  echo "❌ Error: Sección [No Publicado] no encontrada en CHANGELOG.md"
  echo "💡 Agrega la sección al inicio del CHANGELOG"
  exit 1
}
```

### 2. Parsear y validar argumentos

Extraer PRs y tipo de release con validación estricta:

```bash
# Separar PRs de release_type
pr_args=""
release_type=""

for arg in $ARGUMENTS; do
  if [[ "$arg" =~ ^(patch|minor|major)$ ]]; then
    [[ -n "$release_type" ]] && {
      echo "❌ Error: Solo se permite un tipo de release (encontrado: $release_type y $arg)"
      exit 1
    }
    release_type="$arg"
  elif [[ "$arg" =~ ^[0-9,]+$ ]]; then
    pr_args="$pr_args $arg"
  else
    echo "❌ Error: Argumento inválido '$arg'"
    echo "💡 Uso: /changelog [PRs] [patch|minor|major]"
    exit 1
  fi
done

pr_args=$(echo "$pr_args" | tr ',' ' ' | xargs)
```

### 3. Auto-detección o parsing manual de PRs

**Si `pr_args` está vacío (auto-detección):**

```bash
echo "🔍 Auto-detectando PRs faltantes..."

# Crear archivo temporal seguro
tmp_file=$(mktemp)
trap "rm -f '$tmp_file'" EXIT INT TERM

last_pr=$(grep -oE 'PR #[0-9]+' CHANGELOG.md | grep -oE '[0-9]+' | sort -n | tail -1)
[[ -n "$last_pr" ]] || {
  echo "❌ Error: No se encontró PR previo en CHANGELOG"
  echo "💡 Agrega manualmente el primer PR"
  exit 1
}
echo "📍 Último PR documentado: #$last_pr"

# Detectar múltiples formatos de merge (merge, squash, rebase)
git log --pretty=format:"%s" --all | \
  grep -oE '(#[0-9]+|Merge pull request #[0-9]+|\(#[0-9]+\))' | \
  grep -oE '[0-9]+' | sort -n -u | \
  awk -v last="$last_pr" '$1 > last' > "$tmp_file"

pr_list=$(cat "$tmp_file" | tr '\n' ' ' | xargs)
[[ -n "$pr_list" ]] || {
  echo "✓ CHANGELOG actualizado - no hay PRs nuevos posteriores a #$last_pr"
  exit 0
}

new_count=$(echo "$pr_list" | wc -w | xargs)
echo "🔍 Encontrados $new_count PRs nuevos: $pr_list"
```

**Si `pr_args` tiene contenido (modo manual):**

```bash
pr_list="$pr_args"
echo "Procesando PR(s): $pr_list"

# Validar que todos son números
for pr in $pr_list; do
  [[ "$pr" =~ ^[0-9]+$ ]] || {
    echo "❌ Error: '$pr' no es un número de PR válido"
    exit 1
  }
done
```

### 4. Validación y clasificación de PRs

Iterar sobre cada PR, validar en GitHub y clasificar por tipo:

```bash
declare -a prs_added
declare -a prs_changed
declare -a prs_fixed
validated_prs=""

for pr in $pr_list; do
  # Validar PR en GitHub
  pr_data=$(gh pr view "$pr" --json number,state,title 2>/dev/null)
  [[ -n "$pr_data" ]] || {
    echo "❌ Error: PR #$pr no encontrado en GitHub"
    exit 1
  }

  pr_state=$(echo "$pr_data" | jq -r '.state')
  [[ "$pr_state" == "MERGED" ]] || {
    echo "❌ Error: PR #$pr no está mergeado (estado: $pr_state)"
    exit 1
  }

  pr_title=$(echo "$pr_data" | jq -r '.title')
  echo "✓ PR #$pr validado: $pr_title"

  # Detectar duplicados
  if grep -q "(PR #$pr)" CHANGELOG.md; then
    echo "⚠️  PR #$pr ya existe en CHANGELOG - omitido"
    continue
  fi

  # SEGURIDAD: Sanitizar pr_title para prevenir inyección de comandos
  # Escapar caracteres peligrosos para sed: & / \ $
  pr_title_safe=$(printf '%s' "$pr_title" | sed 's/[&/\$]/\\&/g')

  # Clasificar por tipo de commit (Conventional Commits)
  if [[ "$pr_title" =~ ^feat:|^feature: ]]; then
    prs_added+=("$pr:$pr_title_safe")
  elif [[ "$pr_title" =~ ^fix: ]]; then
    prs_fixed+=("$pr:$pr_title_safe")
  elif [[ "$pr_title" =~ ^docs: ]]; then
    echo "⚠️  PR #$pr es documentación - omitido del CHANGELOG"
    continue
  elif [[ "$pr_title" =~ ^(refactor|chore|style):|^perf: ]]; then
    prs_changed+=("$pr:$pr_title_safe")
  else
    prs_changed+=("$pr:$pr_title_safe")
  fi

  validated_prs="$validated_prs $pr"
done

# Verificar que al menos un PR fue validado
[[ -n "$validated_prs" ]] || {
  echo "✓ No hay PRs nuevos para agregar"
  exit 0
}
```

### 5. Insertar en sección [No Publicado]

Para cada categoría (Añadido/Cambiado/Arreglado), insertar PRs en CHANGELOG:

```bash
# Función helper para insertar en sección específica
insert_in_section() {
  local section="$1"
  shift
  local prs=("$@")

  [[ ${#prs[@]} -eq 0 ]] && return

  # Buscar línea "### $section" dentro de [No Publicado]
  section_line=$(awk '/## \[No Publicado\]/,/^## \[/ {
    if (/^### '"$section"'/) print NR
  }' CHANGELOG.md | head -1)

  if [[ -z "$section_line" ]]; then
    # Crear sección si no existe (después de ## [No Publicado])
    unreleased_line=$(grep -n "^## \[No Publicado\]" CHANGELOG.md | cut -d: -f1)
    [[ -n "$unreleased_line" ]] || {
      echo "❌ Error: No se pudo encontrar línea [No Publicado]"
      exit 1
    }

    insert_line=$((unreleased_line + 2))
    [[ $insert_line -gt 0 ]] || {
      echo "❌ Error: Línea de inserción inválida"
      exit 1
    }

    # Insertar header de sección
    sed -i.bak "${insert_line}i\\
### $section\\
" CHANGELOG.md || {
      echo "❌ Error: Falló inserción de sección $section"
      exit 1
    }
    section_line=$((insert_line + 1))
  else
    section_line=$((section_line + 1))
  fi

  # Insertar PRs después del header
  for pr_entry in "${prs[@]}"; do
    pr_num="${pr_entry%%:*}"
    pr_title="${pr_entry#*:}"

    # Limpiar prefijo de tipo (feat:, fix:, etc)
    pr_title=$(echo "$pr_title" | sed -E 's/^(feat|feature|fix|refactor|docs|style|test|chore|perf)(\([^)]+\))?!?:\s*//')

    # Insertar entry (pr_title ya está sanitizado)
    sed -i.bak "${section_line}i\\
- $pr_title (PR #$pr_num)\\
" CHANGELOG.md || {
      echo "❌ Error: Falló inserción de PR #$pr_num"
      exit 1
    }
    section_line=$((section_line + 1))
  done

  rm -f CHANGELOG.md.bak
}

# Insertar en cada sección
insert_in_section "Añadido" "${prs_added[@]}"
insert_in_section "Cambiado" "${prs_changed[@]}"
insert_in_section "Arreglado" "${prs_fixed[@]}"

echo "✅ CHANGELOG.md actualizado con PRs en sección [No Publicado]"
```

### 6. Release automático (opcional)

Si se especificó tipo de release (patch/minor/major):

```bash
if [[ -n "$release_type" ]]; then
  echo "🚀 Ejecutando release $release_type..."

  # Validar que package.json existe y tiene campo version
  [[ -f package.json ]] || {
    echo "❌ Error: package.json no encontrado - release automático no disponible"
    echo "💡 Crea package.json o ejecuta release manual"
    exit 1
  }

  current_version=$(jq -r '.version // empty' package.json)
  [[ -n "$current_version" ]] || {
    echo "❌ Error: package.json no tiene campo 'version'"
    exit 1
  }

  echo "📍 Versión actual: $current_version"

  # Calcular nueva versión con npm version (sin crear tag aún)
  new_version=$(npm version "$release_type" --no-git-tag-version 2>/dev/null | tr -d 'v')
  [[ -n "$new_version" ]] || {
    echo "❌ Error: npm version falló"
    exit 1
  }

  current_date=$(date +%Y-%m-%d)
  echo "📍 Nueva versión: $new_version ($current_date)"

  # Crear backup de CHANGELOG antes de modificar
  cp CHANGELOG.md CHANGELOG.md.backup

  # Reemplazar ## [No Publicado] con ## [X.Y.Z] - YYYY-MM-DD
  sed -i.bak "s/^## \[No Publicado\]/## [$new_version] - $current_date/" CHANGELOG.md || {
    echo "❌ Error: Falló reemplazo de [No Publicado]"
    mv CHANGELOG.md.backup CHANGELOG.md
    exit 1
  }

  # Crear nueva sección [No Publicado] al inicio (después de header principal)
  # Buscar línea después del separador inicial (---)
  header_end=$(grep -n "^---$" CHANGELOG.md | head -1 | cut -d: -f1)
  insert_line=$((header_end + 2))

  sed -i.bak "${insert_line}i\\
## [No Publicado]\\
\\
### Añadido\\
- [Cambios futuros se documentan aquí]\\
\\
---\\
" CHANGELOG.md || {
    echo "❌ Error: Falló creación de nueva sección [No Publicado]"
    mv CHANGELOG.md.backup CHANGELOG.md
    exit 1
  }

  rm -f CHANGELOG.md.bak CHANGELOG.md.backup
  echo "✓ CHANGELOG: [No Publicado] → [$new_version]"

  # Ejecutar npm version (sincroniza README, VitePress, etc)
  echo "🔄 Sincronizando archivos con npm version..."
  npm version "$new_version" --allow-same-version || {
    echo "❌ Error: npm version falló en sincronización"
    exit 1
  }

  echo "✅ Release $release_type completado: v$new_version"
  echo "📝 Commit y tag creados automáticamente"
  echo "💡 Push con: git push origin main --follow-tags"
else
  # Solo commit CHANGELOG.md
  total_prs=$((${#prs_added[@]} + ${#prs_changed[@]} + ${#prs_fixed[@]}))
  [[ $total_prs -gt 0 ]] || {
    echo "✓ No hay cambios para commitear"
    exit 0
  }

  # Verificar estado de git
  changed_files=$(git diff --name-only)
  if [[ "$changed_files" != "CHANGELOG.md" && -n "$changed_files" ]]; then
    echo "⚠️  Advertencia: Otros archivos modificados detectados:"
    echo "$changed_files"
    echo "Solo se commiteará CHANGELOG.md"
  fi

  git add CHANGELOG.md
  commit_msg="docs: update CHANGELOG with PRs $(echo $validated_prs | tr ' ' ',')"

  if ! git commit -m "$commit_msg"; then
    echo "❌ Error: Commit falló"
    exit 1
  fi

  echo "✅ CHANGELOG commiteado"
  echo "💡 Para hacer release: /changelog patch (o minor/major)"
fi
```

### 7. Validación post-actualización

```bash
# Verificar que todos los PRs validados fueron insertados
for pr in $validated_prs; do
  if ! grep -q "(PR #$pr)" CHANGELOG.md; then
    echo "❌ Error: PR #$pr no fue insertado correctamente"
    exit 1
  fi
done

echo "✓ Validación completa - todos los PRs insertados correctamente"
```

## Notas de Seguridad

- **Sanitización de entrada**: Todos los títulos de PR son escapados antes de usar en comandos shell
- **Archivos temporales seguros**: Uso de `mktemp` con cleanup automático via `trap`
- **Validación estricta**: Argumentos, estados de PR, y formato de CHANGELOG validados exhaustivamente
- **Prevención de inyección**: Sin interpolación directa de variables user-controlled en comandos

## Notas Importantes

- **Clasificación automática**: `feat:` → Añadido, `fix:` → Arreglado, `refactor:/chore:/perf:` → Cambiado, `docs:` → omitido
- **Sección [No Publicado]**: Todos los PRs se insertan aquí primero
- **Release automático**: Usar `patch/minor/major` para ejecutar `npm version` y sincronizar todo
- **Sin confirmación**: Comando ejecuta automáticamente sin pedir confirmación
- **Prevención de duplicados**: PRs existentes se omiten automáticamente
- **Manejo de errores robusto**: Backups y rollback en caso de fallo durante release
