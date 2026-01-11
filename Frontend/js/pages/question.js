import { dom } from "./question/dom.js";
import { state } from "./question/state.js";
import { initCatalogSection } from "./question/catalog_section.js";
import { initGenerateSection } from "./question/generate_section.js";
import { initCheckSection } from "./question/check_section.js";
import { initExplainSection } from "./question/explain_section.js";
import { initJsonSection } from "./question/json_section.js";

const catalogApi = initCatalogSection({ dom, state });

catalogApi.loadCatalog();

initGenerateSection({ dom, state, catalogApi });
initCheckSection({ dom, state });

try {
  initExplainSection({ dom, state });
} catch (e) {
  console.error("Explain section init failed", e);
}

try {
  initJsonSection({ dom, state });
} catch (e) {
  console.error("JSON section init failed", e);
}
