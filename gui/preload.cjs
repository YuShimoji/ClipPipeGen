const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("clipPipe", {
  statusEpisode: (episodeDir) => ipcRenderer.invoke("episode:status", episodeDir),
  setCompliance: (payload) => ipcRenderer.invoke("action:setCompliance", payload),
  registerMaterial: (payload) => ipcRenderer.invoke("action:registerMaterial", payload),
  patchThumbnail: (payload) => ipcRenderer.invoke("action:patchThumbnail", payload),
});
