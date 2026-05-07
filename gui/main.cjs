const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("node:path");
const { spawn } = require("node:child_process");
const argsBuilders = require("./args.cjs");

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
      sandbox: true,
    },
  });

  win.loadFile(path.join(__dirname, "renderer.html"));
}

ipcMain.handle("episode:status", async (_event, episodeDir) => {
  return runStatusEpisode(episodeDir || "samples/episode_example");
});

ipcMain.handle("action:setCompliance", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildSetComplianceArgs(payload || {}))
);

ipcMain.handle("action:registerMaterial", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildRegisterMaterialArgs(payload || {}))
);

ipcMain.handle("action:patchThumbnail", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildPatchThumbnailArgs(payload || {}))
);

ipcMain.handle("action:initEditPack", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildInitEditPackArgs(payload || {}))
);

ipcMain.handle("action:validateEditPack", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildValidateEditPackArgs(payload || {}))
);

ipcMain.handle("action:addCutCandidate", async (_event, payload) =>
  safeRunCli(() => argsBuilders.buildAddCutCandidateArgs(payload || {}))
);

function pythonExecutable() {
  return process.env.CLIPPIPEGEN_PYTHON || "python";
}

function spawnPython(args) {
  return new Promise((resolve) => {
    const child = spawn(pythonExecutable(), args, {
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
        code: null,
        stdout,
        stderr,
        error: String(error.message || error),
        argv: args,
      });
    });
    child.on("close", (code) => {
      resolve({ ok: code === 0, code, stdout, stderr, argv: args });
    });
  });
}

function runStatusEpisode(episodeDir) {
  const args = [
    "-m",
    "src.cli.main",
    "status-episode",
    "--episode-dir",
    episodeDir,
    "--format",
    "json",
  ];
  return spawnPython(args).then((result) => {
    if (!result.ok) {
      return {
        ok: false,
        code: result.code,
        error: result.error || result.stderr || "status-episode failed",
        stdout: result.stdout,
        stderr: result.stderr,
      };
    }
    try {
      return { ok: true, status: JSON.parse(result.stdout) };
    } catch (error) {
      return {
        ok: false,
        error: `status-episode returned invalid JSON: ${error.message}`,
        stdout: result.stdout,
        stderr: result.stderr,
      };
    }
  });
}

async function runCli(args) {
  const fullArgs = ["-m", "src.cli.main", ...args];
  const result = await spawnPython(fullArgs);
  return {
    ok: result.ok,
    code: result.code,
    stdout: result.stdout,
    stderr: result.stderr,
    error: result.error,
    argv: result.argv,
    command: ["python", ...fullArgs],
  };
}

async function safeRunCli(buildArgs) {
  try {
    const args = buildArgs();
    return await runCli(args);
  } catch (error) {
    return {
      ok: false,
      code: null,
      stdout: "",
      stderr: "",
      error: String((error && error.message) || error),
      argv: [],
      command: ["python", "-m", "src.cli.main"],
    };
  }
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
