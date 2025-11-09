# Browser Tools Skill

Automatización completa de Chrome/Chromium via CDP (Chrome DevTools Protocol) con Puppeteer API completo.

## Propósito

Control programático total de browser para E2E testing, performance profiling, web scraping, y debugging avanzado.

## Compatibilidad de Plataforma

**⚠️ macOS solamente** - Esta versión actual solo soporta macOS.

**Limitaciones técnicas:**
- Path de Chrome hardcoded: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Comando `rsync` para sincronización de perfil (estándar en macOS)
- Paths de perfil específicos de macOS: `~/Library/Application Support/Google/Chrome/`

**¿Necesitas Linux/Windows?** Abre un issue en [GitHub](https://github.com/Dario-Arcos/ai-framework/issues) para soporte multi-plataforma.

## Capacidades

**Capacidades equivalentes a Playwright MCP:**
- E2E testing (assertions, multi-step flows, waitFor)
- Network interception & mocking
- Performance profiling (Web Vitals, resource timing)
- Coverage analysis (JS/CSS usage)
- Multi-tab orchestration

**Ventaja diferenciadora:** Zero overhead de contexto (0 tokens vs ~15 tools permanentes en MCP).

## Setup (una vez)

**IMPORTANTE:** Ejecuta estos comandos EXACTAMENTE como se muestran:

```bash
# Desde el directorio raíz del plugin ai-framework:
cd skills/browser-tools/tools
npm install

# Verificar instalación exitosa:
ls node_modules/puppeteer-core
```

Si ves "No such file or directory", instalaste en el directorio incorrecto. **Debe ser en `tools/` subdirectory**, no en `skills/browser-tools/`.

**Path completo esperado:**
```
~/.claude/plugins/marketplaces/ai-framework/skills/browser-tools/tools/
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

**5. Cerrar Chrome de debugging:**
```bash
./tools/stop.js               # Cierra SOLO el Chrome del puerto 9223
```

::: danger ⚠️ ADVERTENCIA CRÍTICA
**NUNCA uses `killall "Google Chrome"`** - cerrará TODAS tus sesiones de Chrome activas (incluyendo tu navegación personal).

**Usa siempre `./tools/stop.js`** para cerrar solo la instancia de debugging sin afectar tus sesiones.
:::

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

## Troubleshooting

### Error: "Cannot find package 'puppeteer-core'"

**Causa:** `npm install` ejecutado en directorio incorrecto.

**Solución:**
```bash
# Verifica que estás en tools/, no en browser-tools/
pwd  # Debe mostrar: .../skills/browser-tools/tools

# Si estás en el directorio incorrecto:
cd skills/browser-tools/tools
npm install
```

### Error: Chrome no inicia o no se conecta

**Causa:** Chrome ya corriendo en puerto 9223, o proceso zombie.

**Solución:**
```bash
# Ver si hay proceso en puerto 9223:
lsof -ti :9223

# Si existe, mátalo de forma segura:
./tools/stop.js

# Luego reinicia:
./tools/start.js
```

### Error: "permission denied" al ejecutar scripts

**Causa:** Scripts no tienen permisos de ejecución.

**Solución:**
```bash
chmod +x tools/*.js
```

### Chrome se cerró pero puerto 9223 sigue ocupado

**Causa:** Proceso zombie de Chrome.

**Solución:**
```bash
# Matar específicamente proceso en puerto 9223:
lsof -ti :9223 | xargs kill -9
```

## Referencias

- **Tools completos:** Ver `SKILL.md` para lista completa de comandos
- **Origen:** Adaptado de [agent-commands](https://github.com/mitsuhiko/agent-commands) por Armin Ronacher
