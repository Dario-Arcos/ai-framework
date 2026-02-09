# Agentes

Los agentes son módulos especializados que Claude activa automáticamente cuando detecta contexto relevante. A diferencia de los skills (que tú invocas), los agentes se ejecutan solos al identificar condiciones que los requieren: un code review después de implementar, un análisis de seguridad antes de un merge, o debugging cuando algo falla.

> **Antes de empezar**: lee [Skills](./skills-guide.md) para entender la diferencia entre skills (workflows manuales) y agentes (automáticos).

---

## Referencia rápida

| Agent | Qué hace | Cuándo se activa |
|-------|----------|------------------|
| `code-reviewer` | Review contra plan y standards | Después de completar un step del plan |
| `code-simplifier` | Simplifica código reciente | Automático después de escribir código |
| `edge-case-detector` | Detecta edge cases de producción | Antes de merge, código crítico |
| `performance-engineer` | Optimización y observabilidad | Problemas de rendimiento, monitoring |
| `security-reviewer` | Security review del branch | Antes de merge, PRs |
| `systematic-debugger` | Debugging metódico en 4 fases | Cualquier bug, test failure |

---

## Invocación

**Automática** (Claude decide):
```
"Analiza la seguridad de estos cambios"
```

**Explícita** (tú especificas):
```
# Invocación explícita en inglés (Claude lo entiende mejor así)
"Use the security-reviewer agent"
```

**Paralela** (Task tool):
```
# Invocación explícita en inglés (Claude lo entiende mejor así)
"Launch code-reviewer and security-reviewer in parallel"
```

---

## Revisión de código

### code-reviewer

Review del código completado contra el plan original y coding standards.

**Cuándo se activa:** Después de completar un step numerado del plan.

**Dimensiones de análisis:**
- Plan alignment: ¿la implementación sigue el plan?
- Code quality: patterns, error handling, type safety
- Architecture: SOLID, separation of concerns
- Documentation: comments, docstrings

**Output:** Issues categorizados como Critical / Important / Suggestions

---

### code-simplifier

Simplifica código para mejorar legibilidad y mantenibilidad sin cambiar funcionalidad.

**Cuándo se activa:** Automáticamente después de escribir o modificar código.

**Qué hace:**
- Reduce complejidad y nesting
- Elimina redundancia
- Mejora nombres de variables/funciones
- Evita nested ternaries (prefiere switch/if-else)

Prioriza código explícito sobre código clever.

---

## Seguridad y edge cases

### security-reviewer

Security review de los cambios en el branch actual.

**Cuándo se activa:** Antes de crear PR, cambios en auth/payments/data.

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

**Cuándo se activa:** Antes de merge, código que maneja money/state/data crítica.

**Categorías:**

| Tipo | Ejemplos |
|------|----------|
| Boundary | off-by-one, division by zero, null handling |
| Concurrency | race conditions, deadlocks, TOCTOU |
| Integration | unbounded retry, missing timeout, connection leak |
| Silent failure | swallowed exception, ignored return value |

**Threshold:** Solo reporta issues con confidence ≥0.8.

---

## Debugging y rendimiento

### systematic-debugger

Debugging metódico usando el skill `systematic-debugging`.

**Cuándo se activa:** Cualquier bug, test failure, comportamiento inesperado.

**Las 4 fases:**
1. **Root Cause** — Antes de intentar cualquier fix
2. **Pattern** — Encontrar ejemplos funcionales, comparar
3. **Hypothesis** — Formar teoría, testear mínimamente
4. **Implementation** — Crear test, fix, verificar

**Regla de hierro:** NO fixes sin investigación de root cause primero.

---

### performance-engineer

Optimización de rendimiento y observabilidad.

**Cuándo se activa:** Performance issues, setup monitoring, optimización.

**Capacidades:**
- **Observability:** OpenTelemetry, DataDog, Prometheus/Grafana, RUM
- **Profiling:** CPU (flame graphs), memory (heap, GC), I/O, language-specific
- **Load testing:** k6, JMeter, Gatling, stress testing
- **Core Web Vitals:** LCP, FID, CLS optimization

---

## Combinaciones efectivas

| Escenario | Agents |
|-----------|--------|
| Pre-merge review | `code-reviewer` + `security-reviewer` + `edge-case-detector` |
| Bug investigation | `systematic-debugger` |
| Performance issue | `performance-engineer` |
| Code cleanup | `code-simplifier` (automático) |

**Siguiente paso**: [Integraciones](./integrations.md)

---

::: info Última actualización
**Fecha**: 2026-02-08
:::
