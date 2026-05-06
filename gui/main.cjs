const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("node:path");
const { spawn } = require("node:child_process");

const repoRoot = path.resolve(__dirname, "..");
const smokeMode = process.argv.includes("--smoke");

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 980,
    minHeight: 680,
    title: "ClipPipeGen",
    backgroundColor: "#f6f4ef",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, "renderer.html"));
}

ipcMain.handle("episode:status", async (_event, episodeDir) => {
  return runStatusEpisode(episodeDir || "samples/episode_example");
});

function runStatusEpisode(episodeDir) {
  const python = process.env.CLIPPIPEGEN_PYTHON || "python";
  const args = [
    "-m",
    "src.cli.main",
    "status-episode",
    "--episode-dir",
    episodeDir,
    "--format",
    "json",
  ];

  return new Promise((resolve) => {
    const child = spawn(python, args, {
      cwd: repoRoot,
      windowsHide: true,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      resolve({
        ok: false,
        error: String(error.message || error),
        stderr,
        stdout,
      });
    });
    child.on("close", (code) => {
      if (code !== 0) {
        resolve({ ok: false, code, stderr, stdout });
        return;
      }
      try {
        resolve({ ok: true, status: JSON.parse(stdout) });
      } catch (error) {
        resolve({
          ok: false,
          error: `status-episode returned invalid JSON: ${error.message}`,
          stdout,
          stderr,
        });
      }
    });
  });
}

app.whenReady().then(() => {
  if (smokeMode) {
    console.log("electron smoke: OK");
    app.quit();
    return;
  }
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
