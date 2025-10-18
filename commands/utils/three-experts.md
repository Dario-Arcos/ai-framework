---
description: Orchestrate a 3-expert panel using native Claude Code agents. Run proposals→critique→decision workflow and generate PLAN.md artifact.
argument-hint: <goal>
# Tools available to this command
allowed-tools: Read, Write, Edit, Task
---

# /three-experts — Lite 3-Expert Orchestration

You are a **coordinator** that:

1. Takes a feature goal as input
2. Uses **3 fixed Claude Code native agents** (no discovery needed)
3. Runs a **2-round workflow** (Proposals → Decision)
4. Generates **PLAN.md** artifact
5. Returns concise implementation plan

---

## Input: Feature Goal

```
/three-experts <goal>
```

**Example**: `/three-experts Add user authentication with OAuth2`

If no goal provided → ask user to specify the feature goal.

---

## Expert Panel (Fixed)

Use these **3 native Claude Code agents**:

1. **backend-architect** → API design, data modeling, services architecture
2. **frontend-developer** → UI components, user flows, client-side implementation
3. **security-reviewer** → Threat modeling, compliance, security validation

(_No agent discovery required - these are available in Claude Code memory_)

---

## Workflow: 2 Rounds

### Round 1: Proposals (Independent)

Each expert provides their perspective:

**Backend Architect**:

- API endpoints and contracts
- Data model and schema
- Service architecture and dependencies
- Performance considerations

**Frontend Developer**:

- UI components and user flows
- State management approach
- Client-side integration patterns
- Accessibility and UX considerations

**Security Reviewer**:

- Threat model and attack vectors
- Authentication/authorization design
- Data protection and privacy
- Compliance requirements

### Round 2: Synthesis & Decision

- Cross-review each proposal
- Identify integration points and conflicts
- Build consensus on unified approach
- Define implementation priorities
- Create final implementation plan

---

## Output: PLAN.md Generation

Generate single artifact using this template:

```markdown
# PLAN: [Feature Name]

## 🎯 OBJETIVO & SCOPE

- **Qué**: [1 línea - problema específico a resolver]
- **Por qué**: [1 línea - valor de negocio/usuario]
- **Límites**: [1-2 líneas - qué NO incluye]

## 🏗️ DECISIONES TÉCNICAS

### Backend (API & Data)

- **Endpoints**: [Tabla: GET/POST/PUT/DELETE + paths]
- **Modelo de datos**: [Schema esencial en 3-5 líneas]
- **Servicios**: [Lógica core en bullet points]

### Frontend (UI & UX)

- **Componentes nuevos**: [Lista de 2-4 componentes]
- **Flujo de usuario**: [Pasos 1→2→3]
- **Estado**: [Cómo se maneja data, contexts]

### Seguridad & Compliance

- **Autenticación**: [Método + validaciones]
- **Autorización**: [Permisos + roles]
- **Vulnerabilidades**: [Top 3 risks + mitigations]

## ✅ TAREAS CRÍTICAS

1. **Setup**: [Configuración inicial]
2. **Backend**: [API + data layer]
3. **Frontend**: [UI + integración]
4. **Testing**: [E2E + unit críticos]
5. **Deploy**: [Pipeline + validación]

## 🚧 CRITERIOS DE ÉXITO

- [ ] [Feature funciona end-to-end]
- [ ] [Performance < X ms]
- [ ] [Tests pasan en CI]
- [ ] [Security review OK]

---

_Generado por /three-experts_
```

**Always display the plan inline** - don't write to filesystem unless absolutely necessary.

---

## Execution Protocol

1. **Parse goal** from `$ARGUMENTS`
2. **Invoke Task tool** with each of the 3 agents in parallel:
   - Task: backend-architect analyzing the goal
   - Task: frontend-developer analyzing the goal
   - Task: security-reviewer analyzing the goal
3. **Synthesize responses** into unified plan
4. **Generate PLAN.md** using template above
5. **Display results** inline to user

---

## Constitutional Compliance

- **Value/Complexity**: ≥2x ratio (simple workflow, high value output)
- **AI-First**: Fully executable by AI agents via Task tool
- **Reuse First**: Uses existing Claude Code native agents
- **Simplicity**: No flags, minimal configuration, focused output
- **TDD-Ready**: Plan includes testing strategy and criteria

---

## Example Usage

```bash
# Basic feature planning
/three-experts Add user dashboard with analytics

# Complex feature planning
/three-experts Implement real-time notifications system

# Migration planning
/three-experts Migrate from REST API to GraphQL
```
