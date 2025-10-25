# Language Conventions - Claude Code Components

**Consistency mandate**: Language choice must be intentional and consistent.

---

## Code & AI Instructions

**Language**: **English**

**Applies to**:

- Agent markdown body
- Command workflow instructions
- Hook code comments
- Script docstrings
- SKILL.md instructions
- README.md (technical docs)

**Rationale**:

- International collaboration
- AI training predominantly English
- Technical terminology standardized in English

**Examples**:

```markdown
# Sub-agent body

## Approach

Analyze code for security vulnerabilities using...
```

```python
# Hook code
def validate_input(data):
    """Validates JSON input from Claude Code"""
    pass
```

---

## User-Facing Messages

**Language**: **Spanish**

**Applies to**:

- Error messages (hooks, scripts)
- Success feedback (commands output)
- Help text
- Validation warnings
- Interactive prompts

**Rationale**:

- ai-framework project is Spanish-speaking team
- User experience in native language
- Error debugging faster in native language

**Examples**:

```python
# Hook error message
sys.stderr.write("ERROR: Archivo no encontrado\n")
```

```bash
# Command output
echo "✅ PR created successfully"
echo "❌ Error: No se encontró el branch especificado"
```

---

## Documentation (Human-Facing)

**Language**: **Spanish**

**Applies to**:

- SDD artifacts (spec.md, plan.md, tasks.md)
- Research documents
- Data models
- Quickstart guides
- Checklists user-facing sections

**Exceptions** (keep English):

- Technical terms (API, endpoint, HTTP)
- Framework names (React, FastAPI)
- Command syntax (git, npm, docker)

**Examples**:

```markdown
# spec.md

## Objetivo

Implementar autenticación OAuth2 para API REST...

## Endpoints

- POST /api/auth/login (inicio de sesión)
```

**NOT**:

```markdown
# spec.md (WRONG - mixing languages)

## Goal

Implement OAuth2 authentication for REST API...

## Endpoints

- POST /api/auth/iniciar-sesion
```

---

## Technical Terms (Jargon)

**Rule**: Keep English even in Spanish docs

**Terms to keep in English**:

- API, REST, GraphQL, HTTP
- Framework names: React, Vue, FastAPI, Django
- Tools: git, npm, docker, kubernetes
- Protocols: TCP, SSL, OAuth, JWT
- Data types: string, integer, boolean, JSON
- Programming concepts: callback, promise, async

**Examples**:

```markdown
# Spanish doc with English jargon (CORRECT)

El endpoint POST /api/users retorna un JSON con el token JWT.
La función callback se ejecuta cuando el promise se resuelve.
```

**NOT**:

```markdown
# Translated jargon (WRONG)

El punto final POST /api/usuarios retorna un JSON con el símbolo JWT.
La función de retrollamada se ejecuta cuando la promesa se resuelve.
```

---

## Code Comments

**Language**: **English**

**Rationale**: Code is international, comments travel with code

**Examples**:

```python
# CORRECT
def process_webhook(payload):
    """Process incoming webhook from GitHub"""
    # Extract commit data
    commits = payload.get('commits', [])
```

```python
# WRONG
def process_webhook(payload):
    """Procesa webhook entrante de GitHub"""
    # Extraer datos de commits
    commits = payload.get('commits', [])
```

---

## Logs & Debugging

**Internal logs**: English
**User-visible logs**: Spanish

**Examples**:

```python
# Internal debug log (file/syslog)
item_count = len(items)
logger.debug("Processing %d items" % item_count)

# User-visible error (stderr)
sys.stderr.write("ERROR: No se pudieron procesar los elementos\n")
```

---

## Git Commit Messages

**Language**: **Spanish** (project convention)

**Format**: `tipo: descripción`

**Examples**:

```bash
git commit -m "feat: agregar validación de tokens JWT"
git commit -m "fix: corregir error en autenticación OAuth"
git commit -m "docs: actualizar guía de instalación"
```

---

## Summary Matrix

| Context                | Language | Example                               |
| ---------------------- | -------- | ------------------------------------- |
| **Agent instructions** | English  | "Analyze code for vulnerabilities..." |
| **Command workflows**  | English  | "Execute bash script to..."           |
| **Hook code**          | English  | `def validate_input(data):`           |
| **Error messages**     | Spanish  | `"ERROR: Archivo no encontrado"`      |
| **Success messages**   | Spanish  | `"✅ Operación exitosa"`              |
| **Spec docs (SDD)**    | Spanish  | `## Objetivo: Implementar...`         |
| **Technical jargon**   | English  | `endpoint`, `callback`, `API`         |
| **Code comments**      | English  | `# Extract commit data`               |
| **Internal logs**      | English  | `logger.debug("Processing...")`       |
| **User logs**          | Spanish  | `"ERROR: No se pudo..."`              |
| **Git commits**        | Spanish  | `"feat: agregar validación"`          |

---

## Validation Checklist

Before delivery, verify:

- [ ] Agent/command/skill instructions in English
- [ ] User-facing error messages in Spanish
- [ ] Technical terms NOT translated
- [ ] Code comments in English
- [ ] SDD artifacts in Spanish (spec, plan, tasks)
- [ ] No language mixing in same paragraph

---

**Version**: 1.0.0
