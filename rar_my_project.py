import zipfile
import os

IGNORE_DIRS = {'.venv', 'mobile', 'test', '.vscode', 'server/uploads'}

def zip_project(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            # Пропустить игнорируемые папки
            if any(ignored in foldername.split(os.sep) for ignored in IGNORE_DIRS):
                continue
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, source_dir)
                zipf.write(filepath, arcname)

zip_project('.', 'project_clean.zip')