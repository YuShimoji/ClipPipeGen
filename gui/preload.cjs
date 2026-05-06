const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("clipPipe", {
  statusEpisode: (episodeDir) => ipcRenderer.invoke("episode:status", episodeDir),
});
