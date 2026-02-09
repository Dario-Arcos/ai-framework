// Theme configuration for AI Framework Handbook
// Extends VitePress default theme with custom brand colors

import { h } from "vue";
import DefaultTheme from "vitepress/theme";
import "./custom.css";
import VersionBadge from "./components/VersionBadge.vue";
import HeroDither from "./components/HeroDither.vue";


export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      "home-hero-info-after": () => [h(HeroDither), h(VersionBadge)],
    });
  },
};
