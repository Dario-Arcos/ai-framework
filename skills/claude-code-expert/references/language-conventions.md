# Language Conventions Reference

## Overview

This reference defines language conventions for Claude Code components. Consistency in language choice ensures clarity and maintainability across the codebase.

---

## Code & AI Instructions

**Language**: **English**

**Constraints:**
- You MUST write agent markdown body in English because AI training is predominantly English
- You MUST write command workflow instructions in English because technical documentation is standardized in English
- You MUST write hook code comments in English because code is international
- You MUST write script docstrings in English because this enables international collaboration
- You MUST write SKILL.md instructions in English because AI models understand English best
- You MUST write README.md (technical docs) in English because this is the standard

**Examples:**
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

**Constraints:**
- You MUST write error messages in Spanish because the ai-framework team is Spanish-speaking
- You MUST write success feedback in Spanish because user experience should be in native language
- You MUST write help text in Spanish because this aids user comprehension
- You MUST write validation warnings in Spanish because debugging is faster in native language
- You MUST write interactive prompts in Spanish because this improves user experience

**Examples:**
```python
# Hook error message
sys.stderr.write("ERROR: Archivo no encontrado\n")
```

```bash
# Command output
echo "✅ PR creado exitosamente"
echo "❌ Error: No se encontró el branch especificado"
```

---

## Documentation (Human-Facing)

**Language**: **Spanish**

**Constraints:**
- You MUST write SDD artifacts (spec.md, plan.md, tasks.md) in Spanish because these are for human consumption
- You MUST write research documents in Spanish because the team reads Spanish
- You MUST write data models in Spanish because domain experts read Spanish
- You MUST write quickstart guides in Spanish because users need native language guidance
- You SHOULD keep technical terms in English because translation loses precision

**Exceptions** (keep English):
- Technical terms (API, endpoint, HTTP)
- Framework names (React, FastAPI)
- Command syntax (git, npm, docker)

**Examples:**
```markdown
# spec.md (CORRECT)
## Objetivo
Implementar autenticación OAuth2 para API REST...

## Endpoints
- POST /api/auth/login (inicio de sesión)
```

```markdown
# spec.md (WRONG - mixing languages incorrectly)
## Goal
Implement OAuth2 authentication for REST API...
```

---

## Technical Terms (Jargon)

**Constraints:**
- You MUST keep technical terms in English even in Spanish docs because translation loses precision
- You MUST NOT translate framework names because they are proper nouns
- You MUST NOT translate tool names because they are proper nouns
- You MUST NOT translate protocol names because they are standardized terms

**Terms to keep in English:**
- API, REST, GraphQL, HTTP
- Framework names: React, Vue, FastAPI, Django
- Tools: git, npm, docker, kubernetes
- Protocols: TCP, SSL, OAuth, JWT
- Data types: string, integer, boolean, JSON
- Programming concepts: callback, promise, async

**Examples:**
```markdown
# Spanish doc with English jargon (CORRECT)
El endpoint POST /api/users retorna un JSON con el token JWT.
La función callback se ejecuta cuando el promise se resuelve.
```

```markdown
# Translated jargon (WRONG)
El punto final POST /api/usuarios retorna un JSON con el símbolo JWT.
```

---

## Code Comments

**Language**: **English**

**Constraints:**
- You MUST write code comments in English because code is international
- You MUST write docstrings in English because they travel with code
- You MUST NOT write comments in Spanish because this limits code portability

**Examples:**
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

**Constraints:**
- You MUST write internal logs (file/syslog) in English because developers are international
- You MUST write user-visible logs (stderr) in Spanish because users read Spanish

**Examples:**
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

**Constraints:**
- You MUST write commit messages in Spanish because this is the project convention
- You MUST use format `tipo: descripción` because this follows conventional commits

**Examples:**
```bash
git commit -m "feat: agregar validación de tokens JWT"
git commit -m "fix: corregir error en autenticación OAuth"
git commit -m "docs: actualizar guía de instalación"
```

---

## Summary Matrix

| Context                | Language | Example                               |
|------------------------|----------|---------------------------------------|
| Agent instructions     | English  | "Analyze code for vulnerabilities..." |
| Command workflows      | English  | "Execute bash script to..."           |
| Hook code              | English  | `def validate_input(data):`           |
| Error messages         | Spanish  | `"ERROR: Archivo no encontrado"`      |
| Success messages       | Spanish  | `"✅ Operación exitosa"`              |
| Spec docs (SDD)        | Spanish  | `## Objetivo: Implementar...`         |
| Technical jargon       | English  | `endpoint`, `callback`, `API`         |
| Code comments          | English  | `# Extract commit data`               |
| Internal logs          | English  | `logger.debug("Processing...")`       |
| User logs              | Spanish  | `"ERROR: No se pudo..."`              |
| Git commits            | Spanish  | `"feat: agregar validación"`          |

---

## Troubleshooting

### Language Mixing in Same Paragraph

If document mixes languages incorrectly:
- You SHOULD identify the target audience (technical vs. user)
- You SHOULD use appropriate language for that audience
- You MUST NOT translate technical jargon

### Unclear Which Language to Use

If context is ambiguous:
- You SHOULD ask: "Who will read this?"
- You SHOULD use English for code/AI, Spanish for users
- You MUST follow the summary matrix above

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
