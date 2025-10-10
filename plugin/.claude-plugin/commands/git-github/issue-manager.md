---
allowed-tools: Bash(gh api *), Bash(gh issue *), Bash(gh repo *), Bash(date *), Bash(echo *)
description: Manages and analyzes GitHub issues providing valuable developer insights
---

# GitHub Issue Manager

Manages your GitHub issues by providing intelligent summary of active issues or deep analysis of a specific issue.

## Usage

```bash
/issue-manager                 # Summary of MY active issues
/issue-manager <issue_number>  # Deep analysis of specific issue
```

## Examples

```bash
/issue-manager           # Show summary of issues assigned to me
/issue-manager 85        # Analyze issue #85 in detail
/issue-manager 142       # Analyze issue #142 in detail
```

## Execution

When executing this command, determine mode based on `$ARGUMENTS`:

### Mode A: Active Issues Summary (no arguments)

#### 1. Initial setup

- **Auto-detect repository**: Use `gh api user --jq '.login'` to get current user
- Use `gh repo view --json owner,name` to get owner/repo of current workspace
- If detection fails, show error "❌ No se pudo detectar repositorio GitHub" and terminate
- Show: "📋 Analizando issues activos para @<username> en <owner>/<repo>..."

#### 2. Active issues collection

- Use `gh issue list --assignee "@me" --json number,title,labels,createdAt,updatedAt`
- Get complete list of issues assigned to current user in this repository
- If no issues, show: "✅ No tienes issues activos asignados" and terminate
- Process each issue to extract: number, title, labels, dates, state

#### 3. Intelligent categorization

- **By priority** (based on labels):
  - 🔴 CRITICAL: labels contain "critical", "urgent", "security"
  - 🟡 HIGH: labels contain "high", "important", "bug"
  - 🟢 MEDIUM: labels contain "enhancement", "feature"
  - ⚪ LOW: other issues or without specific labels
- **By age**:
  - 🆕 RECENT: ≤ 3 days
  - ⏰ NORMAL: 4-14 days
  - 🕒 STALE: > 14 days without update
- **By type** (based on labels): bug, enhancement, documentation, question

#### 4. Executive summary generation

- Show dashboard with format:

  ```
  📊 RESUMEN DE ISSUES ACTIVOS

  Total: <count> issues asignados

  🎯 Por Prioridad:
  🔴 Críticos: <count> | 🟡 Altos: <count> | 🟢 Medios: <count> | ⚪ Bajos: <count>

  📅 Por Antigüedad:
  🆕 Recientes (≤3d): <count> | ⏰ Normales (4-14d): <count> | 🕒 Stale (>14d): <count>

  🏷️ Por Tipo:
  🐛 Bugs: <count> | ✨ Features: <count> | 📚 Docs: <count> | ❓ Questions: <count>

  PRÓXIMAS ACCIONES SUGERIDAS:
  [Lista de 3-5 issues más urgentes con números y títulos]
  ```

### Mode B: Deep Issue Analysis (with argument)

#### 1. Input validation

- Validate argument is a valid positive number
- **Auto-detect repository**: Same as Mode A
- Use `gh issue view $issue_number --json number,title,body,labels,createdAt,updatedAt,state,assignees`
- If doesn't exist, show error "❌ Issue #<number> no existe" and terminate
- Show: "🔍 Analizando issue #<number>: <title>..."

#### 2. Complete context extraction

- **Basic information**: number, title, state, labels, assignee, dates
- **Description**: issue body (first 500 characters if very long)
- **Recent activity**: last 3 comments if they exist
- **Related issues**: search mentions to other issues in body and comments
- **Mentioned files**: detect file paths in description and comments

#### 3. Complexity and priority analysis

- **Complexity estimation** (based on content and labels):
  - SIMPLE: minor changes, typos, basic documentation
  - MODERATE: specific bugs, small features
  - COMPLEX: refactoring, architecture, multiple files
- **Urgency level** (based on labels and date):
  - IMMEDIATE: critical labels + recently created
  - HIGH: important bugs or requested features
  - NORMAL: improvements and general maintenance

#### 4. Detailed report

- Show complete analysis with format:

  ```
  🎯 ANÁLISIS DETALLADO - Issue #<number>

  📋 INFORMACIÓN BÁSICA
  Título: <title>
  Estado: <state> | Creado: <created> | Actualizado: <updated>
  Labels: <labels_list>
  Assignee: <assignee>

  📝 DESCRIPCIÓN
  <body_summary>

  🔍 ANÁLISIS TÉCNICO
  Complejidad estimada: <complexity_level>
  Prioridad: <priority_level>
  Archivos potencialmente afectados: <detected_files>

  🔗 CONTEXTO
  Issues relacionados: <related_issues>
  Actividad reciente: <recent_activity_summary>

  ✅ PRÓXIMOS PASOS SUGERIDOS
  [Lista de 3-4 acciones específicas basadas en el análisis]
  ```

## Value Information Provided

### For Active Summary:

- **Complete visibility** of current workload
- **Intelligent prioritization** based on labels and dates
- **Stale issues detection** requiring attention
- **Balanced distribution** of work types
- **Clear next actions** to optimize productivity

### For Individual Analysis:

- **Complete context** of problem/requirement
- **Effort estimation** based on complexity
- **Related files** for technical planning
- **Identified dependencies** with other issues
- **Specific action plan** for efficient resolution

**IMPORTANT**:

- Do not request user confirmation
- Handle GitHub API errors gracefully
- Execute correct mode based on argument presence
- Provide actionable information, not just descriptive
