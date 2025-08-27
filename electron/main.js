const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  // === Меню приложения ===
  const template = [
    {
      label: "Файл",
      submenu: [
        { role: "reload", label: "🔄 Перезагрузить" },
        { role: "quit", label: "🚪 Выйти" }
      ]
    },
    {
      label: "Вид",
      submenu: [
        { role: "toggleDevTools", label: "🛠 DevTools" },
        { role: "togglefullscreen", label: "⛶ Полный экран" }
      ]
    },
    {
      label: "Справка",
      submenu: [
        {
          label: "О программе",
          click: () => {
            mainWindow.webContents.send("log-message", "ℹ️ Telegram Voice Server v1.0.0");
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// ⚡ IPC обработчики
ipcMain.handle("ping", () => {
  return "pong ✅"; // ответ для теста
});

// Запуск Python-сервера
ipcMain.on("start-server", () => {
  if (pythonProcess) {
    mainWindow.webContents.send("log-message", "⚠️ Сервер уже запущен");
    return;
  }

  mainWindow.webContents.send("log-message", "⏳ Запуск Python-сервера...");

  pythonProcess = spawn("python", ["server/app.py"], { cwd: __dirname });

  pythonProcess.stdout.on("data", (data) => {
    mainWindow.webContents.send("log-message", `🟢 ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    mainWindow.webContents.send("log-message", `🔴 ${data}`);
  });

  pythonProcess.on("close", (code) => {
    mainWindow.webContents.send("log-message", `⚠️ Сервер остановился с кодом ${code}`);
    pythonProcess = null;
  });
});

// Остановка сервера
ipcMain.on("stop-server", () => {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
    mainWindow.webContents.send("log-message", "🛑 Сервер остановлен");
  }
});

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});