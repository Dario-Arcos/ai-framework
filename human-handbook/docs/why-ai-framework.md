# Por qué AI Framework

AI Framework es un plugin para Claude Code que convierte prompts sueltos en un proceso de ingeniería con quality gates automáticos, validación de seguridad y desarrollo guiado por scenarios. Esta página explica qué problema resuelve y cómo lo hace.

---

## El problema

Usar un LLM sin estructura produce patrones predecibles de degradación:

### Iteración sin arquitectura

```plaintext
Request: "Implementa autenticación JWT"
Output: Código funcional sin tests
Request: "Agrega refresh tokens"
Output: Modificación sin validación de regresión  // [!code warning]
Request: "Agrega validación"
Output: Parches sobre parches  // [!code error]

Resultado: Código frágil, arquitectura ad-hoc, deuda técnica  // [!code error]
```

### Ausencia de quality gates

- Tests como afterthought (si existen)
- Security reviews manuales e inconsistentes
- Complexity sin control (over-engineering o under-engineering)
- Arquitectura que emerge sin diseño intencional

::: danger Consecuencia
Proyectos que funcionan en desarrollo pero fallan en producción.
:::

---

## La solución

AI Framework aplica gobernanza basada en investigación validada:

### Fundamentos

::: info Context Engineering (Anthropic, 2025)
Optimización de context windows:
- Minimizar tokens, maximizar señal
- Filtrado de false positives validado
- Context loading just-in-time
:::

::: info LLM Optimization (DeepMind OPRO, 2023)
Técnicas con resultados medidos:
- Framing sistemático: **+46.2 puntos** accuracy en el benchmark GSM8K
- Multi-approach analysis: **+57.7% calidad** según el estudio ATLAS (2024)
:::

::: info Scenario-Driven Development (basado en StrongDM Software Factory)
Ciclo scenario-satisfy-refactor:
- **40-80% reducción** en bugs según Microsoft Research (2008, estudio sobre TDD/BDD)
- Prevención de regresiones mediante scenario-first
:::

::: info Constitutional AI (Anthropic, 2022)
Principios como enforcement automático:
- Constraints no negociables (complexity budgets, SDD, reuse-first)
- Separación de responsabilidades (Product, Design, Engineering, Security)
- Audit trail para decisiones arquitectónicas
:::

---

## Arquitectura

El framework aplica enforcement en tres capas:

::: details Constitutional Layer
**Invariantes aplicadas automáticamente:**
- Value/complexity ≥2x (beneficio debe justificar costo)
- SDD mandatory (scenarios antes de código)
- Complexity budgets (S≤80, M≤250, L≤600 líneas netas)
:::

::: details Orchestration Layer
**Componentes especializados:**
- Specialized agents por dominio técnico
- Workflow commands para ciclos reproducibles
- Lifecycle hooks con interception points
- Skills con workflows estructurados
:::

::: details Execution Layer
**Validación continua:**
- Quality gates automáticos (security, performance, constitutional)
- Ejecución paralela con manejo de dependencias
- Audit trail completo
:::

La diferencia con otros enfoques: el framework aplica estas reglas automáticamente, no las sugiere.

---

## Ejemplo: Autenticación

::: code-group

```plaintext [Sin Framework]
Request: "Implementa JWT auth"
Output: Código funcional sin tests  // [!code warning]
Deploy: Funciona en desarrollo
Production: Token expiration no validada → security breach  // [!code error]
```

```plaintext [Con Framework]
Request: "Implementa JWT auth"
SDD gate: Scenario definido antes de implementación  // [!code highlight]
Security review: Detecta falta de token expiration → blocker  // [!code highlight]
Constitutional check: +120 líneas (Size M, dentro de budget)  // [!code highlight]
Output: Feature con tests, vulnerabilidad prevenida, complexity controlada
```

:::

Qué se previene con este flujo:
- Scenarios ausentes (SDD blocker)
- Vulnerabilidades básicas (security review pre-merge)
- Over-engineering (complexity budget)
- Arquitectura inconsistente (agent orchestration)

---

## Transformación: Asistente a ingeniero

::: code-group

```plaintext [Asistente (vanilla)]
Developer → "Haz X" → Claude hace X → "Ahora Y" → Claude hace Y
            [Micro-gestión continua]  // [!code warning]
```

```plaintext [Ingeniero (framework)]
Developer → "Objetivo: Sistema de autenticación"
Framework + Claude:
  ├─ Framing (¿JWT? ¿OAuth? ¿Refresh tokens?)  // [!code highlight]
  ├─ Multi-approach ROI (beneficio vs complejidad)  // [!code highlight]
  ├─ Implementación SDD (scenarios → código)  // [!code highlight]
  ├─ Quality gates (security + code review + constitutional)  // [!code highlight]
  └─ Despliegue (PR auto-creado, reviews aprobados)  // [!code highlight]

[Developer: decisiones estratégicas | Claude: ejecución táctica]
```

:::

::: tip Resultado
El developer deja de micro-gestionar y se enfoca en decisiones de producto y arquitectura.
:::

---

## De idea a producción

::: code-group

```plaintext [Ciclo Tradicional]
Idea → Spec (días) → Design (días) → Dev (semanas) → QA (días)
      [Humanos en cada paso · Errores acumulados · 1-2 meses]  // [!code warning]
```

```plaintext [Claude Code Vanilla]
Idea → Claude genera → Developer corrige → Deploy (quizás)
      [Rápido pero frágil · Sin tests · Días, calidad ?]  // [!code warning]
```

```plaintext [AI Framework]
Idea → Diseño estructurado (minutos)  // [!code highlight]
     → Plan de implementación (minutos)  // [!code highlight]
     → Ejecución con SDD (horas)  // [!code highlight]
     → Dual review → /pullrequest → Despliegue  // [!code highlight]

[Guiado por humanos, ejecutado por IA]
[Tests desde día 1 · Horas-días, production-ready]
```

:::

### Comparación

| Aspecto       | Sin Framework | Con Framework              |
| ------------- | ------------- | -------------------------- |
| Tests         | A veces       | Siempre (SDD enforced)     |
| Seguridad     | Ad-hoc        | Automática (scanning)      |
| Escalabilidad | Se degrada    | Se mantiene (patterns)     |
| Compliance    | Manual        | Automático (budgets)       |

---

## En resumen

Claude Code tiene capacidades potentes, pero sin estructura produce resultados inconsistentes. AI Framework agrega esa estructura: quality gates que bloquean código sin tests, security reviews que detectan vulnerabilidades antes del merge, y complexity budgets que frenan el over-engineering.

Tú decides qué construir. El framework se encarga de que el resultado sea production-ready.

**Siguiente paso**: [Inicio rápido](./quickstart.md)

---

::: info Última actualización
**Fecha**: 2026-02-08
:::
