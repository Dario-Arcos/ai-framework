import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid";

export default withMermaid(defineConfig({
  lang: "es-ES",
  title: "AI Framework Handbook",
  description: "Guía completa para desarrollo AI-first con Claude Code",
  base: "/ai-framework/",
  appearance: true,

  head: [["link", { rel: "icon", href: "/ai-framework/favicon.png" }]],

  themeConfig: {
    version: "5.1.2",
    previousVersion: "5.1.1",

    search: {
      provider: "local",
      options: {
        locales: {
          es: {
            placeholder: "Buscar documentación",
            translations: {
              button: {
                buttonText: "Buscar",
                buttonAriaLabel: "Buscar",
              },
              modal: {
                noResultsText: "Sin resultados para",
                resetButtonTitle: "Limpiar búsqueda",
                footer: {
                  selectText: "Seleccionar",
                  navigateText: "Navegar",
                  closeText: "Cerrar",
                },
              },
            },
          },
        },
      },
    },

    sidebar: [
      {
        text: "Guías",
        collapsed: false,
        items: [
          { text: "Por qué AI Framework", link: "/docs/why-ai-framework" },
          { text: "Inicio rápido", link: "/docs/quickstart" },
          { text: "Workflow", link: "/docs/ai-first-workflow" },
          { text: "Pro tips", link: "/docs/claude-code-pro-tips" },
        ],
      },
      {
        text: "Herramientas",
        collapsed: false,
        items: [
          { text: "Skills", link: "/docs/skills-guide" },
          { text: "Agentes", link: "/docs/agents-guide" },
          { text: "Integraciones", link: "/docs/integrations" },
        ],
      },
      {
        text: "Proyecto",
        collapsed: false,
        items: [
          { text: "Changelog", link: "/docs/changelog" },
        ],
      },
    ],

    outline: {
      label: "En esta página",
    },

    docFooter: {
      prev: "Anterior",
      next: "Siguiente",
    },

    darkModeSwitchLabel: "Apariencia",
  },

  // Mermaid configuration
  mermaid: {
    theme: "neutral",
  },
}));
