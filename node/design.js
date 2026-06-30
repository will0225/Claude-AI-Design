#!/usr/bin/env node
/** View/export design profile — see python/design.py */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import {
  OUTPUT_DIR,
  exportDesignReference,
  loadBrandConfig,
  renderFixedDocument,
  sectionSpecs,
} from "./brand_loader.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const cmd = process.argv[2] ?? "show";
const config = loadBrandConfig();

console.log(`Design ID: ${config.design_id ?? config.company.name}\n`);

if (cmd === "show") {
  console.log(exportDesignReference(config));
} else if (cmd === "export") {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const out = path.join(OUTPUT_DIR, "design-reference.txt");
  fs.writeFileSync(out, exportDesignReference(config) + "\n");
  console.log(`✓ Exported: ${out}`);
} else if (cmd === "preview") {
  const specs = sectionSpecs("report", config);
  const payload = {
    document_title: "Design Preview",
    file_number: "SR-PREVIEW-00",
    review_type: "Design Preview",
    property_address: "000 Sample Boulevard",
    subtitle: "Colors, fonts, and format preview",
    prepared_for: "Preview Client",
    property_contact: "Preview · 000-000-0000",
    review_period: "Preview",
    issued_date: "Preview",
    sections: Object.fromEntries(
      specs.map((s) => [s.slug, `<p>Preview: ${s.name}</p>`])
    ),
  };
  const html = renderFixedDocument(config, "report", payload);
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const out = path.join(OUTPUT_DIR, "design-preview.html");
  fs.writeFileSync(out, html);
  console.log(`✓ Preview: ${out}`);
} else {
  console.log("Usage: node design.js [show|export|preview]");
}
