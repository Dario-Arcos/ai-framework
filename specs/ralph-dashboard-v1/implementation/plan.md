# Implementation Plan: Ralph Dashboard v1

> Plan de implementación ordenado por dependencias

---

## Prerequisites

- [x] Node.js 18+ instalado
- [x] Directorio `dashboard/` en proyecto root
- [x] Archivos de referencia: `status.json`, `logs/metrics.json` (generados por loop.sh)

---

## Implementation Checklist

- [x] Task 01: Project setup + file readers
- [x] Task 02: HTTP server + API endpoint
- [ ] Task 03: HTML dashboard UI
- [ ] Task 04: Integration + polish

---

## Task Details

### Task 01: Project Setup + File Readers

**Complexity:** S (Small)

**Description:**
Crear estructura del proyecto y funciones para leer archivos JSON.

**Acceptance Criteria:**
- [ ] `dashboard/` directory exists
- [ ] `package.json` with start script
- [ ] `readStatusFile()` returns parsed status.json or null
- [ ] `readMetricsFile()` returns parsed metrics.json or null
- [ ] `readRecentLogs(n)` returns last n lines from iteration.log
- [ ] Tests pass for all readers

**TDD Approach:**
1. Write test: `readStatusFile() returns null when file missing`
2. Write test: `readStatusFile() returns object when file exists`
3. Implement function
4. Repeat for metrics and logs

---

### Task 02: HTTP Server + API Endpoint

**Complexity:** S (Small)

**Dependencies:** Task 01

**Description:**
Crear servidor HTTP y endpoint `/api/status`.

**Acceptance Criteria:**
- [ ] Server starts on port 3456
- [ ] GET `/api/status` returns JSON with status, metrics, recentLogs
- [ ] GET `/api/status` returns `{ active: false }` when no loop
- [ ] GET `/` returns 200 (placeholder for now)
- [ ] Tests pass for API responses

**TDD Approach:**
1. Write test: `GET /api/status returns JSON`
2. Write test: `GET /api/status with missing files returns active:false`
3. Implement server
4. Manual test with curl

---

### Task 03: HTML Dashboard UI

**Complexity:** M (Medium)

**Dependencies:** Task 02

**Description:**
Crear interfaz HTML que consume la API y muestra estado.

**Acceptance Criteria:**
- [ ] GET `/` returns HTML page
- [ ] Page shows status section (iteration, status, branch)
- [ ] Page shows metrics section (total, success, failed, rate)
- [ ] Page shows recent logs section (last 10 entries)
- [ ] Auto-refresh every 2s via fetch
- [ ] Visual indicators for status (colors, icons)
- [ ] "No loop active" state renders correctly

**TDD Approach:**
1. Write test: `GET / returns HTML content-type`
2. Manual testing in browser for UI

---

### Task 04: Integration + Polish

**Complexity:** S (Small)

**Dependencies:** Task 03

**Description:**
Testing end-to-end, edge cases, documentación.

**Acceptance Criteria:**
- [ ] Works with real loop.sh output
- [ ] Handles file not found gracefully
- [ ] Handles malformed JSON gracefully
- [ ] README.md with usage instructions
- [ ] `npm start` works from dashboard/

**TDD Approach:**
1. Create mock status.json files for testing
2. Verify all edge cases in browser

---

## Rollout Plan

1. **Development**: Implementar en `dashboard/` subdirectory
2. **Testing**: Ejecutar con loop de prueba
3. **Integration**: Documentar en ralph-orchestrator skill

---

## Success Metrics

- [ ] Total LOC < 200
- [ ] 0 external dependencies (solo Node stdlib)
- [ ] Dashboard funciona en <5s de startup
- [ ] Auto-refresh funciona sin errores

---

*Plan ready for task generation*
