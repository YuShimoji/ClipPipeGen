const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const required = [
  "gui/main.cjs",
  "gui/preload.cjs",
  "gui/renderer.html",
  "gui/renderer.js",
  "gui/styles.css",
  "package.json",
];

for (const file of required) {
  const full = path.join(root, file);
  if (!fs.existsSync(full)) {
    throw new Error(`missing ${file}`);
  }
}

const html = fs.readFileSync(path.join(root, "gui/renderer.html"), "utf8");
for (const id of ["view-episode", "view-rights", "view-materials", "view-thumbnail", "view-settings"]) {
  if (!html.includes(id)) {
    throw new Error(`renderer missing ${id}`);
  }
}

const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
if (!pkg.devDependencies || !pkg.devDependencies.electron) {
  throw new Error("electron devDependency is missing");
}

console.log("gui smoke: OK");
