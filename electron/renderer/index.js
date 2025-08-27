const form = document.getElementById("cfg");
const logEl = document.getElementById("log");
const startBtn = document.getElementById("start");
const stopBtn  = document.getElementById("stop");
const openFlaskBtn = document.getElementById("openflask");

function toObj(formData) {
  const o = {};
  for (const [k, v] of formData.entries()) o[k] = v;
  return o;
}
function setForm(values) {
  [...form.elements].forEach(el => {
    if (!el.name) return;
    if (values[el.name] !== undefined) el.value = values[el.name];
  });
}
function appendLog(line) {
  logEl.textContent += (typeof line === "string" ? line : JSON.stringify(line)) + "";
  if (!logEl.textContent.endsWith("\n")) logEl.textContent += "\n";
  logEl.scrollTop = logEl.scrollHeight;
}

(async () => {
  const cfg = await window.API.loadConfig();
  setForm(cfg || {});
})();

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const ok = await window.API.saveConfig(toObj(new FormData(form)));
  if (ok) appendLog("✅ Конфигурация сохранена.");
});

startBtn.addEventListener("click", async () => {
  appendLog("⏳ Запуск сервисов...");
  await window.API.startServices();
});

stopBtn.addEventListener("click", async () => {
  await window.API.stopServices();
});

openFlaskBtn.addEventListener("click", async () => {
  await window.API.openUrl("http://127.0.0.1:5000");
});

window.API.onLog(appendLog);