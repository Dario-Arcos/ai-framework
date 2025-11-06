# Browser Automation Skill

Automatización completa de Chrome/Chromium via CDP (Chrome DevTools Protocol) con Puppeteer API completo.

## Propósito

Control programático total de browser para E2E testing, performance profiling, web scraping, y debugging avanzado.

**Capacidades equivalentes a Playwright MCP:**
- E2E testing (assertions, multi-step flows, waitFor)
- Network interception & mocking
- Performance profiling (Web Vitals, resource timing)
- Coverage analysis (JS/CSS usage)
- Multi-tab orchestration

**Ventaja diferenciadora:** Zero overhead de contexto (0 tokens vs ~15 tools permanentes en MCP).

## Setup (una vez)

```bash
cd skills/browser-automation/tools
npm i
```

## Uso Típico

**1. Iniciar Chrome con debugging:**
```bash
./tools/start.js              # Perfil temporal, puerto 9223
./tools/start.js --profile    # Copia tu perfil (cookies, logins)
```

::: tip Aislamiento Seguro
Usa puerto `:9223` (aislado de tu Chrome principal en `:9222`). **No cierra tus sesiones activas.**
:::

**2. Navegar:**
```bash
./tools/nav.js https://example.com
```

**3. Extraer datos:**
```bash
./tools/eval.js 'document.querySelectorAll("h1")[0].textContent'
```

**4. Screenshot:**
```bash
./tools/screenshot.js         # Devuelve path a archivo temp
```

## Casos de Uso Avanzados

**E2E Testing:**
- Assertions personalizadas (page.evaluate + if/throw)
- Multi-step user flows (login, checkout, forms)
- Visual regression (screenshots comparativos)

**Performance Auditing:**
- Web Vitals extraction (FCP, LCP, TTFB)
- Resource waterfall analysis
- Third-party script impact measurement

**Web Scraping:**
- SPAs con contenido dinámico
- Sitios que requieren JS execution
- Extracción de datos estructurados

**Debugging Programático:**
- Network interception & mocking
- Coverage analysis (JS/CSS usage)
- Memory profiling (heap usage, leak detection)

## Cuándo Usar

✅ **Usa este skill:**
- Context budget crítico (zero overhead)
- Necesitas JavaScript arbitrario
- E2E testing ad-hoc o exploratorio
- Profiling/debugging programático
- Scraping complejo

❌ **Usa Playwright MCP:**
- Testing continuo (browser siempre disponible)
- Prefieres API calls vs escribir código
- Necesitas tools pre-empaquetados

## Referencias

- **Tools completos:** Ver `SKILL.md` para lista completa de comandos
- **Origen:** Adaptado de [agent-commands](https://github.com/mitsuhiko/agent-commands) por Armin Ronacher
