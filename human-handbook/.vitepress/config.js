import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "es-ES",
  title: "Trivance AI Handbook",
  description: "Guía completa para desarrollo AI-first con Claude Code",
  base: "/ai-framework/",
  appearance: true,

  head: [["link", { rel: "icon", href: "/ai-framework/favicon.png" }]],

  themeConfig: {
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
          { text: "Tips Pro", link: "/docs/claude-code-pro-tips" },
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
