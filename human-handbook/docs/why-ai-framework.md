# Por qué AI Framework

Claude Code es capaz. El problema es que sus capacidades se degradan de formas predecibles cuando trabajas sin estructura, y la mayoría de esas degradaciones son invisibles hasta que ya es tarde.

---

## Qué sale mal sin estructura

Esto no es teórico. Son patrones que se repiten en sesiones reales:

### El modelo deja de usar las herramientas que tiene

Vercel midió esto en 2026: en el 56% de los casos, Claude no invocó skills disponibles aunque tenía acceso a ellos. El modelo tenía la documentación correcta a un tool call de distancia, pero decidió que no la necesitaba. El resultado fue código basado en APIs deprecadas que compilaba pero fallaba en runtime.

No es un bug. Es una limitación medida de cómo los modelos deciden cuándo usar herramientas.

### El contexto se degrada en sesiones largas

Cada token en el context window compite por atención con todos los demás (escalamiento n² en la arquitectura de atención). En la práctica: las instrucciones que diste en el turno 3 se pierden para el turno 40. El modelo empieza a repetir búsquedas, olvida decisiones arquitectónicas, y la calidad cae sin que nadie lo note.

### "Funciona" no significa que funcione

Le pides que implemente algo, te dice "listo", y el código se ve razonable. Pero no lo ejecutó. No verificó edge cases. No revisó que los scenarios previos sigan pasando. "It should work" es la frase más cara en ingeniería de software, y los modelos la usan todo el tiempo si no les exiges evidencia.

---

## Qué hace el framework

AI Framework es un plugin de Claude Code que inyecta gobernanza en cada sesión. No son sugerencias que el modelo puede ignorar — son constraints embebidos a nivel de system prompt que el modelo recibe antes de leer tu primer mensaje.

### Gobernanza constitucional

Al iniciar cada sesión, un hook de SessionStart lee un conjunto de constraints y los inyecta como contexto de sistema. El modelo recibe reglas como "nunca hagas push sin autorización" o "nunca empieces trabajo multi-step sin un task plan" como parte de su contexto base, no como una instrucción que puede decidir ignorar.

Esto se complementa con un mecanismo de enforcement que invierte la carga de prueba para usar skills: en vez de "¿debería invocar este skill?", el modelo opera con "solo salta el skill si estás seguro de que no aplica." Esto reduce el 56% de no-invocación que Vercel midió.

### Scenario-Driven Development

El framework exige que definas qué debería pasar antes de escribir código. No tests — scenarios. La diferencia importa: un test dice `assert split(100, 20, 4) == 30.0`. Un scenario dice "4 amigos dividen $100 con 20% de propina, cada uno paga $30."

El test se puede manipular (el modelo reescribe el assertion para que pase). El scenario no, porque vive fuera del código. El code-reviewer agent verifica que los scenarios se definieron antes de la implementación y detecta reward hacking — cuando el modelo reescribe validaciones para que coincidan con su output.

### Sub-agents con contexto limpio

Cuando una tarea es compleja, el framework la delega a sub-agents que arrancan con un context window limpio de 200k tokens. El agente principal recibe un resumen de 1-2k tokens. Esto previene la degradación de contexto que ocurre cuando una sola sesión acumula 50k+ tokens de historial.

### Agents especializados

Seis agents se activan automáticamente según el contexto:

- **code-reviewer** revisa después de cada implementación. Verifica que los scenarios se definieron primero y detecta reward hacking.
- **systematic-debugger** exige diagnóstico en 4 fases antes de proponer cualquier fix. Previene el patrón de "cambiar cosas hasta que funcione."
- **security-reviewer** analiza el diff de tu branch buscando vulnerabilidades explotables.
- **edge-case-detector** busca boundary violations, race conditions, y resource leaks después de cada implementación.
- **performance-engineer** analiza cuando hay bottlenecks o problemas de escalabilidad.
- **code-simplifier** reduce complejidad preservando funcionalidad.

### Skills como workflows

24 skills cubren el ciclo completo: desde brainstorming y discovery hasta implementación con SDD, commits inteligentes, y pull requests. Cada skill es un workflow estructurado que se carga cuando el contexto lo requiere — no un template estático.

Ralph, el orchestrator, puede ejecutar proyectos multi-step de forma autónoma: planifica, genera tareas, ejecuta con verificación doble, y tiene circuit breakers que detienen la ejecución si detecta loops o thrashing.

---

## Qué cambia en la práctica

Sin framework, la dinámica es: tú le dices qué hacer, Claude lo hace, tú revisas, repites. Micro-gestión constante. Si te descuidas, el modelo toma atajos que no notas hasta producción.

Con framework, la dinámica cambia: tú defines qué quieres lograr, el framework se asegura de que el proceso sea riguroso. Los scenarios se definen antes del código. Los reviews pasan automáticamente. La evidencia de ejecución se exige antes de marcar algo como completo.

No es que Claude no pueda hacer buen trabajo sin esto. Es que la probabilidad de que lo haga consistentemente, sesión tras sesión, proyecto tras proyecto, sin estructura que lo gobierne, es baja. El framework sube esa probabilidad.

---

## Fundamentos técnicos

El framework se apoya en investigación verificable:

- **Context engineering** (Anthropic, 2025): optimización de context windows. Contexto pasivo supera a retrieval activo. Un index comprimido de 8KB rinde igual que 40KB de documentación completa.
- **Scenario-Driven Development** (basado en StrongDM Software Factory): scenarios como holdouts externos que el modelo no puede manipular, a diferencia de tests que viven dentro del código.
- **Passive context superiority** (Vercel, 2026): AGENTS.md estáticos alcanzan 100% pass rate donde skills invocables logran 53%. La lección: embeber contexto funciona mejor que depender de que el modelo decida buscarlo.

---

## Siguiente paso

[Inicio rápido](./quickstart.md)

---

::: info Última actualización
**Fecha**: 2026-02-10
:::
