# Agents

Especialistas AI para tareas complejas. Claude los invoca automáticamente o puedes especificarlos.

---

## Referencia rápida

| Agent | Qué hace | Cuándo usarlo |
|-------|----------|---------------|
| `code-reviewer` | Review contra plan y standards | Después de completar un step del plan |
| `code-simplifier` | Simplifica código reciente | Automático después de escribir código |
| `edge-case-detector` | Detecta edge cases de producción | Antes de merge, código crítico |
| `performance-engineer` | Optimización y observabilidad | Problemas de rendimiento, monitoring |
| `security-reviewer` | Security review del branch | Antes de merge, PRs |
| `systematic-debugger` | Debugging metódico 4 fases | Cualquier bug, test failure |
| `test-automator` | Test automation moderno | Estrategia de tests, frameworks |

---

## Invocación

**Automática** (Claude decide):
```
"Analiza la seguridad de estos cambios"
```

**Explícita** (tú especificas):
```
"Use the security-reviewer agent"
```

**Paralela** (Task tool):
```
"Launch code-reviewer and security-reviewer in parallel"
```

---

## Code Review & Quality

### code-reviewer

Review de código completado contra el plan original y coding standards.

**Cuándo usarlo:** Después de completar un step numerado del plan.

**Dimensiones de análisis:**
- Plan alignment: ¿implementación sigue el plan?
- Code quality: patterns, error handling, type safety
- Architecture: SOLID, separation of concerns
- Documentation: comments, docstrings

**Output:** Issues categorizados como Critical / Important / Suggestions

---

### code-simplifier

Simplifica código para claridad y mantenibilidad sin cambiar funcionalidad.

**Cuándo se activa:** Automáticamente después de escribir o modificar código.

**Qué hace:**
- Reduce complejidad y nesting
- Elimina redundancia
- Mejora nombres de variables/funciones
- Evita nested ternaries (prefiere switch/if-else)

**Principio:** Claridad sobre brevedad. Código explícito > código clever.

---

## Security & Edge Cases

### security-reviewer

Security review de los cambios en el branch actual.

**Cuándo usarlo:** Antes de crear PR, cambios en auth/payments/data.

**Categorías que examina:**
- Input validation: SQL injection, command injection, XXE
- Auth: bypass, privilege escalation, JWT vulnerabilities
- Secrets: hardcoded keys, weak crypto
- Code execution: deserialization, eval injection, XSS

**Metodología:**
1. Repository context (patterns existentes)
2. Comparative analysis (desviaciones)
3. Vulnerability assessment (data flow tracing)

**Threshold:** Solo reporta issues con >80% confidence de exploitability.

---

### edge-case-detector

Detecta edge cases que causan production failures.

**Cuándo usarlo:** Antes de merge, código que maneja money/state/data crítica.

**Categorías:**

| Tipo | Ejemplos |
|------|----------|
| Boundary | off-by-one, division by zero, null handling |
| Concurrency | race conditions, deadlocks, TOCTOU |
| Integration | unbounded retry, missing timeout, connection leak |
| Silent failure | swallowed exception, ignored return value |

**Threshold:** Solo reporta issues con confidence ≥0.8.

---

## Debugging & Performance

### systematic-debugger

Debugging metódico usando el skill `systematic-debugging`.

**Cuándo usarlo:** Cualquier bug, test failure, comportamiento inesperado.

**Las 4 fases:**
1. **Root Cause** — Antes de intentar cualquier fix
2. **Pattern** — Encontrar ejemplos funcionales, comparar
3. **Hypothesis** — Formar teoría, testear mínimamente
4. **Implementation** — Crear test, fix, verificar

**Regla de hierro:** NO fixes sin investigación de root cause primero.

---

### performance-engineer

Optimización de rendimiento y observabilidad.

**Cuándo usarlo:** Performance issues, setup monitoring, optimización.

**Capacidades:**
- **Observability:** OpenTelemetry, DataDog, Prometheus/Grafana, RUM
- **Profiling:** CPU (flame graphs), memory (heap, GC), I/O, language-specific
- **Load testing:** k6, JMeter, Gatling, stress testing
- **Core Web Vitals:** LCP, FID, CLS optimization

---

## Testing

### test-automator

Test automation con frameworks modernos y AI-powered testing.

**Cuándo usarlo:** Definir estrategia de tests, implementar test suites.

**Frameworks que domina:**
- JS/TS: Jest, Vitest, Playwright, Cypress
- Python: pytest, Robot Framework
- Java: JUnit 5, TestNG, Cucumber
- Mobile: Appium, Detox

**Estrategias:**
- Test pyramid: 70% unit, 20% integration, 10% E2E
- Contract testing: Pact
- Visual testing: Applitools, Percy
- Self-healing tests: automatic selector updates

---

## Combinaciones efectivas

| Escenario | Agents |
|-----------|--------|
| Pre-merge review | `code-reviewer` + `security-reviewer` + `edge-case-detector` |
| Bug investigation | `systematic-debugger` |
| Performance issue | `performance-engineer` |
| Test strategy | `test-automator` |
| Code cleanup | `code-simplifier` (automático) |

---

::: info Última actualización
**Fecha**: 2026-01-31 | **Agents**: 7 total
:::
