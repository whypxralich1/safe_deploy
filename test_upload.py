"""
Тестирование загрузки файлов
"""

import requests
import os

BASE_URL = "http://localhost:8000"

def test_upload_valid_file():
    """Тест загрузки валидного PNG файла"""
    print("\n🧪 Тест 1: Загрузка валидного PNG файла")

    # Создаем простой PNG (минимальный валидный PNG)
    # В реальности используйте реальный PNG файл
    headers = {"X-Username": "alice"}

    # Если у вас есть реальный PNG файл, раскомментируйте:
    # with open("test.png", "rb") as f:
    #     files = {"file": ("test.png", f, "image/png")}
    #     response = requests.post(f"{BASE_URL}/files/upload", headers=headers, files=files)

    print("   Используйте curl для тестирования:")
    print(f"   curl -X POST {BASE_URL}/files/upload -H 'X-Username: alice' -F 'file=@test.png'")

def test_upload_fake_image():
    """Тест загрузки fake.jpg (текстового файла)"""
    print("\n🧪 Тест 2: Загрузка fake.jpg (текстовый файл с расширением .jpg)")

    headers = {"X-Username": "alice"}

    # Создаем fake.jpg
    with open("fake.jpg", "w") as f:
        f.write("This is not a real JPEG image")

    with open("fake.jpg", "rb") as f:
        files = {"file": ("fake.jpg", f, "image/jpeg")}
        response = requests.post(f"{BASE_URL}/files/upload", headers=headers, files=files)

    if response.status_code == 400:
        print(f"✅ PASS: Сервер отклонил fake.jpg (Status: {response.status_code})")
        print(f"   Message: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Ожидался 400, получен {response.status_code}")
        print(f"   Response: {response.text}")

def test_upload_large_file():
    """Тест загрузки большого файла (>2 МБ)"""
    print("\n🧪 Тест 3: Загрузка большого файла (>2 МБ)")

    headers = {"X-Username": "alice"}

    # Создаем большой файл
    with open("large.txt", "wb") as f:
        f.write(b"X" * (3 * 1024 * 1024))  # 3 МБ

    with open("large.txt", "rb") as f:
        files = {"file": ("large.txt", f, "image/png")}
        response = requests.post(f"{BASE_URL}/files/upload", headers=headers, files=files)

    if response.status_code == 413:
        print(f"✅ PASS: Сервер отклонил большой файл (Status: {response.status_code})")
        print(f"   Message: {response.json()['detail']}")
    else:
        print(f"❌ FAIL: Ожидался 413, получен {response.status_code}")

def test_download_file():
    """Тест скачивания файла"""
    print("\n🧪 Тест 4: Скачивание файла")

    headers = {"X-Username": "alice"}
    response = requests.get(f"{BASE_URL}/files/1/download", headers=headers)

    if response.status_code == 200:
        print(f"✅ PASS: Файл скачан (Status: {response.status_code})")
        print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔒 ТЕСТИРОВАНИЕ ЗАГРУЗКИ ФАЙЛОВ")
    print("=" * 60)

    test_upload_valid_file()
    test_upload_fake_image()
    test_upload_large_file()
    test_download_file()
