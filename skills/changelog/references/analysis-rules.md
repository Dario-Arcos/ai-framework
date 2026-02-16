# Analysis Rules Reference

## Análisis por Tipo de Archivo

| Tipo | Qué Buscar | Categoría |
|------|------------|-----------|
| **Código** | Funciones/clases nuevas | Añadido |
| | Funciones modificadas | Cambiado |
| | Funciones eliminadas | Eliminado (¿breaking?) |
| | Validaciones/edge cases | Arreglado |
| | Sanitización/auth | Seguridad |
| **Config** | Opciones nuevas | Añadido |
| | Opciones modificadas | Cambiado |
| | Opciones eliminadas | Eliminado (¿breaking?) |
| **Docs** | Guías nuevas | Añadido |
| | Updates sustanciales | Cambiado |
| | Solo typos | Skip |
| **CI/CD** | Pipeline nueva | Añadido |
| | Pipeline modificada | Cambiado |
| | Step eliminado | Cambiado |
| **Docker** | Imagen base cambiada | Cambiado (¿breaking?) |
| | Puerto expuesto cambiado | Cambiado |
| | Variable de entorno requerida | Añadido |
| **Migrations** | Tabla/columna nueva | Añadido |
| | Columna eliminada | Eliminado (breaking) |
| | Tipo de dato cambiado | Cambiado (¿breaking?) |
| **Tests** | Tests nuevos para feature existente | Skip (test infra) |
| | Tests que revelan nuevo comportamiento | Documentar comportamiento |
| **Dependencies** | Runtime dep añadida | Añadido (si expone API) |
| | Runtime dep major bump | Cambiado (¿breaking?) |
| | Dev-dep changes | Skip |

> **Patrones de archivo por tipo:**
> - CI/CD: `.github/*`, `Jenkinsfile`, `.gitlab-ci.yml`
> - Docker: `Dockerfile`, `docker-compose.*`
> - Migrations: `migrations/*`, archivos de schema
> - Tests: `*.test.*`, `*.spec.*`
> - Dependencies: `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`

## Filtrado Señal/Ruido

Basado en los principios de [Common Changelog](https://common-changelog.org).

### EXCLUIR siempre

- Dotfiles de desarrollo (`.gitignore`, `.editorconfig`, `.prettierrc`)
- Actualizaciones de dev-dependencies exclusivamente
- Cambios de formateo/estilo sin cambio semántico (lint fixes)
- Lock files (`package-lock.json`, `yarn.lock`, `Cargo.lock`)
- Build artifacts (`dist/`, `build/`, `coverage/`)
- Archivos generados automáticamente

### INCLUIR siempre

- Refactors que cambian API pública o comportamiento observable
- Cambios de runtime/versión mínima soportada
- Documentación de features que antes no estaban documentadas
- Cambios en valores por defecto
- Correcciones de seguridad (cualquier severidad)

### EVALUAR caso por caso

- Refactors internos (incluir si hay side effects posibles)
- Cambios de CI/CD (incluir si afectan el artefacto publicado)
- Cambios en README/docs (incluir si documentan features nuevas)

## Detección de Breaking Changes

```yaml
breaking_signals:
  - Función/método público eliminado
  - Cambio de firma (parámetros requeridos añadidos/removidos)
  - Cambio de tipo de retorno
  - Opción de config requerida eliminada
  - Cambio de comportamiento por defecto
  - API endpoint removido o cambiado
  - Variable de entorno removida/renombrada
  - Flag de CLI cambiado o removido
  - Formato de archivo de configuración cambiado
  - Runtime mínimo aumentado (Node.js, Python, etc.)
  - Puerto o protocolo por defecto cambiado
  - Esquema de base de datos incompatible
```

## Agrupación

### Ejemplo básico

```
Archivos modificados:
├── hooks/anti_drift.py (M)
├── docs/claude-rules/hooks.md (M)
└── tests/test_anti_drift.py (M)

→ UNA entrada:
"Refactorizado hook anti_drift con validación mejorada"

NO tres entradas separadas.
```

### Ejemplo monorepo

```
Archivos modificados (monorepo):
├── packages/core/src/auth.ts (M)
├── packages/core/src/types.ts (M)
├── packages/cli/src/commands/login.ts (M)
├── packages/web/src/hooks/useAuth.ts (M)
├── docs/authentication.md (M)
└── packages/core/tests/auth.test.ts (M)

→ UNA entrada:
"Refactorizado sistema de autenticación con soporte OAuth 2.0 (PR #456)"

NO seis entradas separadas por archivo.
```

### Criterios de agrupación

- Mismo módulo/componente
- Mismo PR asociado
- Mismo scope funcional

### Criterios de ordenamiento

Dentro de cada categoría (Añadido, Cambiado, Eliminado, etc.):

1. **Breaking changes primero** — siempre al inicio de la categoría correspondiente
2. **Por alcance de impacto** — cambios que afectan a más usuarios van antes
3. **Por scope funcional** — agrupar entradas relacionadas de forma contigua

---

*Version: 2.0.0 | Updated: 2026-02-16*
