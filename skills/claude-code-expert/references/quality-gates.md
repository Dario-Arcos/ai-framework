# Quality Gates - Claude Code Components

**Aplicable a**: Sub-agents, Commands, Hooks, MCP integrations

## Gate 1: Syntax Validation (Automated)

**Validator**: `scripts/validate_*.py`

**Criteria**:

- YAML/JSON syntax correcta
- Campos requeridos presentes
- Tipos de datos correctos
- No trailing commas, no syntax errors

**Responsabilidad**: Script (automático)

---

## Gate 2: Security Validation (Automated + Manual)

**Validator**: Scripts + Manual review

**Criteria**:

- No hardcoded credentials (>20 chars sin ${VAR})
- Variables quoted en bash (`"$var"` no `$var`)
- No eval() o exec() sin justificación
- Subprocess sin shell=True (o justificado)
- Input validation presente

**Responsabilidad**: Script detecta patterns, humano valida contexto

---

## Gate 3: Logic Consistency (AI-Powered)

**Validator**: AI Self-Review (SKILL.md Step 6)

**Criteria**:

- Variables definidas antes de uso
- Branches completos (if/then/fi)
- Error paths incluyen cleanup
- Tool invocations después de context load
- No circular dependencies

**Responsabilidad**: Claude ejecutando skill

---

## Gate 4: Constitutional Compliance (Manual)

**Reference**: `@.specify/memory/constitution.md`

**Criteria**:

- Value/Complexity ≥ 2
- Reuse First (existing patterns)
- AI-First design (text/JSON interfaces)
- TDD (if applicable)
- No over-engineering

**Responsabilidad**: Humano + AI review

---

## Gate 5: Integration Validation (Manual)

**Criteria**:

- Component integra con proyecto existente
- No duplicate names
- Category/paths correctos
- Dependencies disponibles

**Responsabilidad**: Humano

---

## Gate 6: Production Readiness (Final Sign-Off)

**The Ultimate Test**:

> **"Would you bet your professional reputation on this working correctly in production?"**

**If YES**: Deliver
**If NO**: Fix and re-validate

**Criteria**:

- All gates passed
- No TODO/FIXME left
- Tested against real scenarios (if possible)
- Documentation complete

**Responsabilidad**: Humano (final accountability)
