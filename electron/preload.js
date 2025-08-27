// preload.js
const { contextBridge, ipcRenderer, shell } = require("electron");

contextBridge.exposeInMainWorld("api", {
  // Тест: проверить связь
  ping: () => ipcRenderer.invoke("ping"),

  // Можно открыть внешний URL в браузере
  openExternal: (url) => shell.openExternal(url),

  // Пример отправки данных из рендера в main
  sendMessage: (channel, data) => {
    ipcRenderer.send(channel, data);
  },

  // Пример получения событий из main
  onMessage: (channel, callback) => {
    ipcRenderer.on(channel, (event, args) => callback(args));
  },
});