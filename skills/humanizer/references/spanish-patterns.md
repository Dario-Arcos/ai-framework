# Spanish AI Writing Patterns

Full reference for detecting and fixing AI-generated text in Spanish. Each pattern includes vocabulary to watch, why it's a problem, and before/after examples.

Sources: RAE (Real Academia Española), AESLA/RAEL linguistic study, Wikipedia WikiProject AI Cleanup, UCM corpus analysis, Fundación Comillas.

---

## 1. Vocabulario inflado (Lexical Bloat)

**Sustantivos abstractos:** ámbito, panorama, paradigma, sinergia, ecosistema, entorno, paisaje, marco, contexto, dinámica

**Adjetivos:** robusto, holístico, transversal, integral, innovador, transformador, dinámico, vital, fundamental, ejemplar, vibrante

**Verbos:** potenciar, impulsar, fomentar, facilitar, maximizar, optimizar, alinear, ampliar, articular

**Calcos del inglés:** "tapiz de emociones" (tapestry of emotions), "catalizar el cambio" (catalyze change), "desbloquear el potencial" (unlock potential), "embarcarse en" (embark on), "ahondar" (delve)

**Por qué es problema:** Los LLM traducen literalmente preferencias léxicas del inglés SEO-optimizado. El resultado es un registro "corporativo-académico" que ningún hispanohablante usa en prosa real. Estudio AESLA confirmó que GPT-3.5 y GPT-4 usan significativamente más adjetivos únicos que los humanos en español.

**Antes:**
> La empresa se posiciona como un catalizador de innovación en el ámbito de la transformación digital, impulsando soluciones robustas e integrales que potencian la sinergia entre equipos transversales.

**Después:**
> La empresa apuesta por la innovación digital. Sus herramientas conectan mejor a los equipos y simplifican el trabajo del día a día.

---

## 2. Gerundio de posterioridad

**Frases a vigilar:** logrando así, generando un efecto, posicionándose como, contribuyendo al desarrollo, mejorando la experiencia, reflejando la importancia

**Por qué es problema:** En español, el gerundio expresa acción simultánea o anterior al verbo principal. El "gerundio de posterioridad" es incorrecto según la RAE y la Nueva Gramática. María Moliner: "el manejo del gerundio es uno de los puntos delicados del uso del español; su abuso revela siempre pobreza de recursos." Los LLM heredan este error del inglés, donde -ing funciona diferente.

**Antes:**
> Vinicius anotó el segundo gol, logrando un importante triunfo para Brasil.

**Después:**
> Vinicius anotó el segundo gol y le dio a Brasil un triunfo importante.

**Antes:**
> La empresa lanzó el producto en diciembre, posicionándose como líder del mercado en el primer trimestre.

**Después:**
> La empresa lanzó el producto en diciembre y se convirtió en líder del mercado en el primer trimestre.

---

## 3. Aperturas formulaicas

**Frases a vigilar:** "En un mundo cada vez más...", "En la era de...", "En el contexto actual...", "En el panorama actual...", "Hoy en día...", "A medida que avanzamos hacia...", "En un entorno en constante evolución...", "Imagina que...", "Es importante entender que..."

**Por qué es problema:** Aperturas "seguras" que aparecen millones de veces en datos de entrenamiento. No aportan información, retrasan el contenido real. Un humano abre con el dato, la anécdota, o la tesis.

**Antes:**
> En un mundo cada vez más digitalizado, las empresas necesitan adaptarse a las nuevas tecnologías para seguir siendo competitivas en el mercado global.

**Después:**
> El 72% de las pymes españolas no tienen presencia digital. Las que la tienen facturan el doble.

**Antes:**
> En la era de la inteligencia artificial, la educación enfrenta desafíos sin precedentes que requieren soluciones innovadoras.

**Después:**
> Un profesor de Sevilla descubrió que la mitad de los trabajos de su clase los había escrito ChatGPT. Esto es lo que hizo después.

---

## 4. Abuso de conectores y marcadores discursivos

**Adición:** Además, Asimismo, Del mismo modo, Igualmente, De igual forma, Por otro lado

**Concesión:** Sin embargo, No obstante, A pesar de ello

**Consecuencia:** Por lo tanto, Por ende, En consecuencia, Consecuentemente

**Énfasis metalingüístico:** Cabe destacar que, Es importante señalar que, Vale la pena mencionar que, En este sentido, En definitiva, Como hemos visto

**Cierre:** En conclusión, En resumen, En síntesis

**Por qué es problema:** La IA coloca un conector en casi cada párrafo, incluso cuando la relación lógica no lo exige. El efecto es un texto que "suena a redacción escolar": mecánico, predecible, con cadencia de metrónomo.

**Antes:**
> Es importante señalar que el cambio climático afecta a todos. Asimismo, cabe destacar que las emisiones de CO2 han aumentado. Por lo tanto, resulta imprescindible tomar medidas. En este sentido, diversos expertos coinciden en que es necesario actuar. En conclusión, el futuro del planeta depende de nuestras decisiones.

**Después:**
> El cambio climático nos afecta a todos. Las emisiones de CO2 siguen subiendo y no hay señales de freno. Toca actuar, y no mañana.

---

## 5. Evitación de la cópula "ser"

**Frases a vigilar:** constituye un referente, se erige como, se posiciona como, se consolida como, se configura como, se presenta como, representa un hito

**Por qué es problema:** Los LLM evitan "ser" porque su entrenamiento penaliza repetición. El resultado: nada "es" algo — todo "se erige como", "se constituye en". En español natural, "ser" es el verbo más común del idioma y su uso directo es signo de claridad, no de pobreza.

**Antes:**
> La biblioteca se erige como un pilar fundamental de la comunidad, constituyendo un espacio que se posiciona como referente cultural y se consolida como catalizador del conocimiento.

**Después:**
> La biblioteca es el corazón del barrio. Allí la gente lee, estudia y se encuentra.

---

## 6. Énfasis excesivo en la importancia

**Frases a vigilar:** juega un papel fundamental/crucial/vital, desempeña un rol crucial/determinante, resulta imprescindible/indispensable, reviste especial importancia, se destaca como un testimonio de, subraya su importancia, deja un impacto duradero

**Por qué es problema:** Los LLM asignan importancia trascendental a cualquier tema. Un pueblo "representa la resiliencia de una comunidad", un parque "refleja la renovación ecológica". En la escritura humana, la importancia se demuestra con datos, no con adjetivación superlativa.

**Antes:**
> La gastronomía local desempeña un rol crucial en la preservación de la identidad cultural, constituyendo un pilar fundamental que resulta imprescindible para la cohesión social.

**Después:**
> En este pueblo se cocina con las mismas recetas desde hace tres siglos. Las abuelas enseñan a las nietas, y así sigue.

---

## 7. Paralelismo negativo "No solo... sino también"

**Frases a vigilar:** No solo X, sino también Y. No se trata solo de X, es Y. No únicamente X, sino además Y.

**Por qué es problema:** Wikipedia lo documenta: "las construcciones paralelas negativas se están sobreexplotando en la prosa generada por IA." Recurso retórico legítimo que la IA usa en casi cada párrafo. En texto humano, aparece una o dos veces como clímax.

**Antes:**
> El festival no solo celebra la música tradicional, sino que también representa un testimonio del patrimonio cultural inmaterial de la región, consolidándose no solo como evento artístico, sino también como catalizador del turismo sostenible.

**Después:**
> El festival lleva 40 años celebrando música tradicional. Además, se ha convertido en el mayor atractivo turístico de la comarca.

---

## 8. Conclusiones genéricas positivas

**Frases a vigilar:** Sin duda alguna, El futuro es prometedor, Queda claro que, En definitiva, Sin lugar a dudas, Lo que está claro es que, Solo el tiempo dirá, El camino por recorrer es largo pero prometedor

**Por qué es problema:** RLHF premia respuestas "útiles y positivas". El resultado: un cierre que podría pegarse a cualquier texto. La escritura humana cierra con dato, pregunta abierta, o simplemente para.

**Antes:**
> Sin duda alguna, la inteligencia artificial transformará profundamente la educación. El futuro es prometedor y queda claro que las posibilidades son infinitas.

**Después:**
> Nadie sabe todavía si la IA mejorará la educación o la empeorará. Lo que sí sabemos es que ya está aquí, y los profesores van a ciegas.

---

## 9. Atribuciones vagas

**Frases a vigilar:** Según expertos, Diversos estudios señalan, Los informes de la industria sugieren, Argumentan algunos críticos, Los expertos coinciden en que, Según investigaciones recientes

**Por qué es problema:** La IA no puede citar fuentes reales (o las fabrica), así que recurre a atribuciones genéricas. En texto humano, se cita al experto por nombre o se reconoce que no se tiene el dato.

**Antes:**
> Según diversos expertos, el consumo de café podría tener beneficios significativos para la salud. Estudios recientes sugieren que su consumo moderado está asociado a una reducción del riesgo cardiovascular.

**Después:**
> Un metaanálisis de 2024 del European Heart Journal, con datos de 1.2 millones de personas, encontró que beber 3 tazas de café al día reduce el riesgo cardiovascular un 15%.

---

## 10. Inconsistencia de registro

**Patrones a vigilar:**
- Mezcla de "tú" y "usted" en el mismo texto
- Saltos entre voseo, tuteo y ustedeo
- Español neutro artificial que no corresponde a ninguna variedad dialectal real
- Mezcla de español peninsular y latinoamericano ("vale" + "chido"; "coche" + "carro")
- Párrafo formal académico seguido de tono coloquial

**Por qué es problema:** ChatGPT genera un "español de laboratorio" que mezcla variedades dialectales. Un hablante real mantiene consistencia: o tutea o ustedea, pero no alterna aleatoriamente.

**Antes:**
> Debes tener en cuenta que esta herramienta le permitirá optimizar sus procesos. Tu equipo encontrará que se adapta a sus necesidades.

**Después (tuteo consistente):**
> Ten en cuenta que esta herramienta te va a simplificar el trabajo. Tu equipo verá que se adapta a lo que necesitan.

---

## 11. Regla de tres mecánica

**Patrones a vigilar:** Tres adjetivos en serie ("creativo, innovador y versátil"), tres sustantivos ("educación, cultura y tecnología"), tres verbos ("potenciar, impulsar y fomentar"), enumeraciones de exactamente tres elementos en cada punto.

**Por qué es problema:** La IA aplica la regla de tres de forma sistemática y caricaturesca. En texto humano, las enumeraciones varían: a veces son dos, a veces cuatro, a veces una sola con matiz.

**Antes:**
> El proyecto busca ser innovador, inclusivo y sostenible, promoviendo la creatividad, la colaboración y el desarrollo, mediante estrategias dinámicas, integrales y transformadoras.

**Después:**
> El proyecto apuesta por la inclusión y la sostenibilidad. El diseño se hizo con 14 vecinos del barrio.

---

## 12. Adjetivación superlativa genérica

**Frases a vigilar:** impresionante, vibrante, majestuoso, rico patrimonio, visita obligada, impresionante belleza natural, ubicado en el corazón de

**Por qué es problema:** La IA aplica los mismos adjetivos a cualquier tema. Un humano usa adjetivos específicos y concretos; la IA recurre a una paleta reducida de calificativos universalmente positivos.

**Antes:**
> Ubicado en el corazón de la región, este impresionante pueblo ofrece una vibrante escena cultural y un rico patrimonio histórico que lo convierte en una visita obligada.

**Después:**
> El pueblo tiene 800 habitantes, una iglesia románica del siglo XII y un bar donde los viejos juegan al dominó cada tarde.

---

## 13. Uniformidad tonal y ausencia de errores

**Patrones a vigilar:** Cero errores tipográficos, longitud de oraciones uniforme (20-25 palabras), estructura de párrafos idéntica (introducción-desarrollo-cierre), estructura predictiva (definición - importancia - tipos - ventajas - conclusión).

**Por qué es problema:** Los humanos cometen errores involuntarios y varían el ritmo. La ausencia total de errores combinada con cadencia monótona es señal clara de generación automática. La escritura humana tiene "ráfagas" de oraciones cortas seguidas de largas, con ritmo irregular.

**Antes:**
> La inteligencia artificial ha revolucionado múltiples sectores industriales. Su capacidad para procesar grandes volúmenes de datos permite identificar patrones complejos. Las organizaciones que adoptan estas tecnologías obtienen ventajas competitivas significativas. El futuro promete avances aún más importantes en este campo.

**Después:**
> La IA ya está en todo. En las fábricas. En los hospitales. En tu móvil. Y aún así, la mayoría de empresas no saben para qué la quieren. Spoiler: muchas no la necesitan.

---

## 14. Cadenas de adverbios en -mente

**Patrones a vigilar:** fundamentalmente, esencialmente, significativamente, particularmente, indudablemente, notablemente. Dos o más adverbios en -mente en la misma oración o párrafo.

**Por qué es problema:** Las guías de estilo recomiendan limitar los adverbios en -mente a uno por párrafo. La IA los encadena porque son "safe tokens" en el modelo probabilístico. El resultado es texto pesado y pedante.

**Antes:**
> Resulta fundamentalmente necesario implementar efectivamente las estrategias previamente diseñadas para significativamente mejorar los resultados académicos.

**Después:**
> Hay que aplicar bien las estrategias que ya tenemos para que los resultados mejoren de verdad.

---

## 15. Formato excesivo

**Patrones a vigilar:** Negritas en múltiples frases por párrafo, emojis decorativos, residuos Markdown (encabezados ##, tablas con |, bloques de código con backticks), listas numeradas que empiezan en "1." en vez del formato nativo, parámetros de rastreo `utm_source=chatgpt.com` en URLs.

**Por qué es problema:** Wikipedia lo documenta como primera señal de texto copiado de un chat con IA. "Un humano suele marcar una o dos ideas clave; la IA muestra varias frases en negrita."

---

## 16. Fuentes fabricadas

**Patrones a vigilar:** DOI que no existen, ISBN inválidos, URLs con `utm_source=chatgpt.com`, citas de fuentes reales pero irrelevantes, marcadores rotos (`:contentReference[oaicite:0]`), placeholders (`[URL of reliable source]`).

**Por qué es problema:** La IA "alucina" referencias para dar apariencia de credibilidad. Wikipedia ha detectado múltiples artículos con DOI fabricados.

---

## 17. Hedging excesivo con "poder"

**Frases a vigilar:** podría tener beneficios, puede contribuir a, podría representar, es posible que, cabe la posibilidad de que

**Por qué es problema:** RLHF entrena a los LLM para evitar afirmaciones categóricas. El resultado: texto lleno de hedging que no se compromete con nada. En español real, el autor afirma cuando tiene evidencia y duda cuando no la tiene, con variación natural.

**Antes:**
> El consumo moderado de café podría tener beneficios significativos que podrían contribuir a una mejora en la salud cardiovascular.

**Después:**
> Tres tazas de café al día bajan el riesgo cardiovascular un 15%, según el European Heart Journal.

---

## Sources

- [RAE - Gerundio de posterioridad](https://www.rae.es/libro-estilo-justicia/las-palabras-y-sus-grupos-problemas-y-actuaciones/gerundio/usos-incorrectos/gerundio-de-posterioridad)
- [AESLA/RAEL - Estudio exploratorio GPT vs humanos en español](https://matrix.aesla.org.es/RAEL/article/view/666)
- [UCM - Corpus comparable humanos vs IA](https://docta.ucm.es/rest/api/core/bitstreams/35114b65-3dbe-4613-b4d7-caa8bc2ba299/content)
- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Wikipedia:WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup)
- [Genbeta - Palabras que delatan ChatGPT](https://www.genbeta.com/inteligencia-artificial/estas-palabras-frases-tus-textos-dejan-claro-has-usado-chatgpt)
- [Infobae - Señales de texto escrito por IA](https://www.infobae.com/tecno/2025/03/29/cinco-senales-en-un-mensaje-que-indican-que-fue-escrito-por-una-ia-no-por-una-persona/)
- [Fundación Comillas - Gerundio de posterioridad](https://fundacioncomillas.es/2019/09/26/gerundio-de-posterioridad/)

---

*Version: 1.0.0 | Updated: 2026-02-11*
