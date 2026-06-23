import requests
import time

BASE_URL = "http://localhost:8000"

FILE_IDS = {
    "alice_report": 1,
    "bob_report": 2,
    "admin_audit": 3
}


def test_get_file_as_owner():
    print("\n🧪 Test 1: Владелец получает свой файл")
    headers = {"X-Username": "alice"}
    response = requests.get(f"{BASE_URL}/files/{FILE_IDS['alice_report']}", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Владелец получил свой файл (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_get_file_as_other_user():
    print("\n🧪 Test 2: IDOR - Алиса пытается получить файл Боба")
    headers = {"X-Username": "alice"}
    response = requests.get(f"{BASE_URL}/files/{FILE_IDS['bob_report']}", headers=headers)
    if response.status_code == 404:
        print(f"✅ PASS: Доступ запрещен (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 404, получен {response.status_code}")
        return False


def test_admin_get_any_file():
    print("\n🧪 Test 3: Админ получает файл Боба")
    headers = {"X-Username": "admin"}
    response = requests.get(f"{BASE_URL}/files/{FILE_IDS['bob_report']}", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Админ получил файл (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_get_my_files():
    print("\n🧪 Test 4: Алиса получает список своих файлов")
    headers = {"X-Username": "alice"}
    response = requests.get(f"{BASE_URL}/files/my", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Получены файлы (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_admin_delete_file():
    print("\n🧪 Test 5: Админ удаляет файл Боба")
    headers = {"X-Username": "admin"}
    response = requests.delete(f"{BASE_URL}/files/{FILE_IDS['bob_report']}", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Админ удалил файл (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_owner_delete_own_file():
    print("\n🧪 Test 6: Алиса удаляет свой файл")
    headers = {"X-Username": "alice"}
    response = requests.delete(f"{BASE_URL}/files/{FILE_IDS['alice_report']}", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Владелец удалил свой файл (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_admin_get_all_files():
    print("\n🧪 Test 7: Админ получает список всех файлов")
    headers = {"X-Username": "admin"}
    response = requests.get(f"{BASE_URL}/files/all", headers=headers)
    if response.status_code == 200:
        print(f"✅ PASS: Админ получил все файлы (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 200, получен {response.status_code}")
        return False


def test_user_cannot_get_all_files():
    print("\n🧪 Test 8: Алиса пытается получить список всех файлов")
    headers = {"X-Username": "alice"}
    response = requests.get(f"{BASE_URL}/files/all", headers=headers)
    if response.status_code == 403:
        print(f"✅ PASS: Доступ запрещен (Status: {response.status_code})")
        return True
    else:
        print(f"❌ FAIL: Ожидался 403, получен {response.status_code}")
        return False


def run_all_tests():
    print("=" * 60)
    print("🔒 ЗАПУСК ТЕСТОВ БЕЗОПАСНОСТИ")
    print("=" * 60)
    print(f"📡 Сервер: {BASE_URL}")

    try:
        response = requests.get(f"{BASE_URL}/files/my", headers={"X-Username": "alice"})
        print("✅ Сервер доступен")
    except:
        print("❌ ОШИБКА: Сервер не запущен!")
        return False

    tests = [
        ("Владелец получает свой файл", test_get_file_as_owner()),
        ("IDOR: Алиса пытается получить файл Боба", test_get_file_as_other_user()),
        ("Админ получает файл Боба", test_admin_get_any_file()),
        ("Получение списка своих файлов", test_get_my_files()),
        ("Админ удаляет файл Боба", test_admin_delete_file()),
        ("Владелец удаляет свой файл", test_owner_delete_own_file()),
        ("Админ получает список всех файлов", test_admin_get_all_files()),
        ("Пользователь не может получить все файлы", test_user_cannot_get_all_files()),
    ]

    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 60)

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for name, result in tests:
        print(f"{'✅ PASS' if result else '❌ FAIL'} - {name}")

    print("-" * 60)
    print(f"Результат: {passed}/{total} тестов пройдено")
    return passed == total


if __name__ == "__main__":
    print("\n🚀 Запуск тестов безопасности...")
    time.sleep(1)
    success = run_all_tests()
    exit(0 if success else 1)
