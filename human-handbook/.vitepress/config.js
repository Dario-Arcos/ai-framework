import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "es-ES",
  title: "AI Framework Handbook",
  description: "Guía completa para desarrollo AI-first con Claude Code",
  base: "/ai-framework/",
  appearance: true,

  head: [["link", { rel: "icon", href: "/ai-framework/favicon.png" }]],

  themeConfig: {
    version: "4.1.0",
    previousVersion: "4.0.0",

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
        text: "Guides",
        collapsed: false,
        items: [
          { text: "Inicio Rápido", link: "/docs/quickstart" },
          { text: "AI-First Workflow", link: "/docs/ai-first-workflow" },
          { text: "Pro Tips", link: "/docs/claude-code-pro-tips" },
          { text: "Memory Systems", link: "/docs/memory-systems" },
        ],
      },
      {
        text: "Tools",
        collapsed: false,
        items: [
          { text: "Comandos", link: "/docs/commands-guide" },
          { text: "Agentes", link: "/docs/agents-guide" },
          { text: "Skills", link: "/docs/skills-guide" },
          { text: "MCP Servers", link: "/docs/mcp-servers" },
        ],
      },
      {
        text: "Project",
        collapsed: false,
        items: [
          { text: "Por Qué AI Framework", link: "/docs/why-ai-framework" },
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
});
