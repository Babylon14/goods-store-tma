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

