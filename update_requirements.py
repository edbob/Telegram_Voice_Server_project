import os
import re

# Папки, которые считаем рабочими
WORK_DIRS = ["bot", "server"]

# Путь к файлу requirements.txt
REQ_FILE = "requirements.txt"

# Существующие зависимости
if os.path.exists(REQ_FILE):
    with open(REQ_FILE, "r", encoding="utf-8") as f:
        existing_requirements = set(line.strip().lower() for line in f if line.strip())
else:
    existing_requirements = set()

# Паттерн для поиска импортов
import_pattern = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)")

found_packages = set()

for work_dir in WORK_DIRS:
    if not os.path.exists(work_dir):
        continue
    for root, dirs, files in os.walk(work_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        match = import_pattern.match(line)
                        if match:
                            pkg = match.group(1).split(".")[0]
                            found_packages.add(pkg)

# Убираем встроенные модули Python
try:
    import stdlib_list
    builtin_modules = set(stdlib_list.stdlib_list("3.11"))
except ImportError:
    builtin_modules = set()

external_packages = {pkg for pkg in found_packages if pkg not in builtin_modules}

# Новые пакеты
new_requirements = external_packages - existing_requirements

if new_requirements:
    with open(REQ_FILE, "a", encoding="utf-8") as f:
        for pkg in sorted(new_requirements):
            f.write(pkg + "\n")
    print(f"✅ Добавлены новые пакеты в {REQ_FILE}: {', '.join(sorted(new_requirements))}")
else:
    print("📦 Новых пакетов не найдено.")