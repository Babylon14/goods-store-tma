import os
import uuid
import shutil

from fastapi import UploadFile


UPLOAD_DIR = "uploads"

async def save_upload_file(upload_file: UploadFile, folder: str = "products") -> str:
    """Сохраняет файл и возвращает путь к нему"""

    # 1. Создаем подпапку (например, uploads/products)
    dest_folder = os.path.join(UPLOAD_DIR, folder)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 2. Геенерируем уникальное имя: uuid + оригинальное расширение
    file_extension = os.path.splitext(upload_file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(dest_folder, file_name)

    # 3. Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # 4. Возвращаем путь, который будет храниться в БД
    return f"/static/{folder}/{file_name}"


def delete_file(file_url: str | None):
    """Удаляет файл с диска, если он существует"""
    if not file_url:
        return

    # Превращаем URL (/static/products/file.jpg) в реальный путь на диске
    # Убираем начальный /static и заменяем на uploads
    if file_url.startswith("/static/"):
        relative_path = file_url.replace("/static/", "uploads/", 1)
        # Получаем полный путь относительно корня (backend/)
        full_path = os.path.abspath(relative_path)
        
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as err:
            print(f"Ошибка при удалении файла {full_path}: {err}")

