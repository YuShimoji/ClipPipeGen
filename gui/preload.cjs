const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("clipPipe", {
  statusEpisode: (episodeDir) => ipcRenderer.invoke("episode:status", episodeDir),
  readPreviewPack: (episodeDir) => ipcRenderer.invoke("preview:read", episodeDir),
  setCompliance: (payload) => ipcRenderer.invoke("action:setCompliance", payload),
  registerMaterial: (payload) => ipcRenderer.invoke("action:registerMaterial", payload),
  patchThumbnail: (payload) => ipcRenderer.invoke("action:patchThumbnail", payload),
  initEditPack: (payload) => ipcRenderer.invoke("action:initEditPack", payload),
  validateEditPack: (payload) => ipcRenderer.invoke("action:validateEditPack", payload),
  addCutCandidate: (payload) => ipcRenderer.invoke("action:addCutCandidate", payload),
});
