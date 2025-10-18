import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "es-ES",
  title: "AI Framework Handbook",
  description: "Guía completa para desarrollo AI-first con Claude Code",
  base: "/ai-framework/",
  appearance: true,

  head: [["link", { rel: "icon", href: "/ai-framework/favicon.png" }]],

  themeConfig: {
    version: "1.3.0",
    previousVersion: "1.1.2",

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
        text: "Guía Rápida",
        items: [
          { text: "Inicio Rápido", link: "/docs/quickstart" },
          { text: "MCP Servers", link: "/docs/mcp-servers" },
          { text: "Pro Tips", link: "/docs/claude-code-pro-tips" },
        ],
      },
      {
        text: "Workflows",
        items: [{ text: "AI-First Workflow", link: "/docs/ai-first-workflow" }],
      },
      {
        text: "Referencia",
        items: [
          { text: "Comandos", link: "/docs/commands-guide" },
          { text: "Agentes", link: "/docs/agents-guide" },
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
