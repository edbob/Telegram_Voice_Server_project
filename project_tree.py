import os
import re

# ==== НАСТРОЙКИ ====
WORK_DIRS = ["bot", "server", "."]  # Папки, которые считаются рабочими
IGNORE_DIRS = ["__pycache__", ".git", ".venv"]
SHOW_ONLY_FOLDER = ["uploads", "icons"]  # Эти папки показывать, но без содержимого
OUTPUT_FILE = "project_tree.txt"

def get_file_comment(filepath):
    """Определяет комментарий по импортам в файле."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return "← Python-скрипт"

    comment_parts = []
    if "flask" in content.lower():
        comment_parts.append("Flask веб-сервер")
    if "telethon" in content.lower() or "telegram" in content.lower():
        comment_parts.append("работа с Telegram API")
    if "gtts" in content.lower() or "tts" in content.lower():
        comment_parts.append("Text-to-Speech")
    if "pygame" in content.lower():
        comment_parts.append("работа с аудио")
    if "langdetect" in content.lower():
        comment_parts.append("определение языка")
    if re.search(r"requests", content):
        comment_parts.append("HTTP-запросы")

    return f"← {', '.join(comment_parts)}" if comment_parts else "← Python-скрипт"

def build_tree(start_path="."):
    project_name = os.path.basename(os.path.abspath(start_path))
    tree_lines = [f"{project_name}/"]  # Добавляем название проекта в начало

    for root, dirs, files in os.walk(start_path):
        rel_path = os.path.relpath(root, start_path)

        # Пропускаем игнорируемые директории
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        # Фильтрация только рабочих папок
        if rel_path != "." and not any(rel_path.startswith(w) for w in WORK_DIRS):
            continue
        
        # Добавляем папку в дерево
        level = rel_path.count(os.sep) + 1  # +1 потому что проект — это 0 уровень
        indent = "│   " * (level - 1)
        folder_name = os.path.basename(root) if rel_path != "." else project_name
        if rel_path != ".":
            tree_lines.append(f"{indent}├── {folder_name}/")

        # Обрабатываем файлы
        for file in sorted(files):
            file_path = os.path.join(root, file)

            # Если папка в списке SHOW_ONLY_FOLDER, то содержимое не показываем
            if os.path.basename(root) in SHOW_ONLY_FOLDER:
                continue

            # Добавляем комментарии к Python-файлам
            if file.endswith(".py"):
                comment = get_file_comment(file_path)
                tree_lines.append(f"{indent}│   └── {file}    {comment}")
            else:
                tree_lines.append(f"{indent}│   └── {file}")

    return "\n".join(tree_lines)

if __name__ == "__main__":
    tree_str = build_tree(".")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(tree_str)

    print(f"Структура проекта сохранена в {OUTPUT_FILE}")