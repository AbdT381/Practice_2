import os
import sys
from urllib.parse import urlparse

# Используем tomllib (Python 3.11+)
try:
    import tomllib
except ImportError:
    print("Ошибка: Для работы скрипта требуется Python 3.11 или выше (модуль tomllib).")
    sys.exit(1)

CONFIG_FILE = "config.toml"

def validate_config(config: dict) -> dict:
    """Валидирует параметры конфигурации и выбрасывает ValueError при ошибках."""
    errors = []

    # 1. Проверка package_name
    package_name = config.get("package_name")
    if not package_name or not isinstance(package_name, str):
        errors.append("Ошибка: 'package_name' должен быть непустой строкой.")

    # 2. Проверка repo_url
    repo_url = config.get("repo_url")
    if not repo_url or not isinstance(repo_url, str):
        errors.append("Ошибка: 'repo_url' должен быть строкой (URL или путь к файлу).")
    else:
        # Проверяем, является ли это валидным URL или существующим локальным путем
        parsed_url = urlparse(repo_url)
        is_url = all([parsed_url.scheme, parsed_url.netloc])
        is_path = os.path.exists(repo_url)
        if not (is_url or is_path):
            errors.append(f"Предупреждение/Ошибка: 'repo_url' ('{repo_url}') не является валидным URL или существующим локальным путем.")

    # 3. Проверка mode
    mode = config.get("mode")
    valid_modes = ["git", "local", "zip"]
    if mode not in valid_modes:
        errors.append(f"Ошибка: 'mode' должен быть одним из следующих значений: {valid_modes}.")

    # 4. Проверка output_image
    output_image = config.get("output_image")
    if not output_image or not isinstance(output_image, str):
        errors.append("Ошибка: 'output_image' должен быть строкой (имя файла).")
    elif not output_image.endswith(('.png', '.jpg', '.jpeg', '.svg')):
        errors.append("Ошибка: 'output_image' должен иметь расширение графического формата (png, jpg, svg).")

    # 5. Проверка max_depth
    max_depth = config.get("max_depth")
    if max_depth is None or not isinstance(max_depth, int) or max_depth < 0:
        errors.append("Ошибка: 'max_depth' должен быть неотрицательным целым числом (>= 0).")

    if errors:
        raise ValueError("\n".join(errors))
    
    return config

def main():
    # Проверка наличия файла конфигурации
    if not os.path.exists(CONFIG_FILE):
        print(f"Ошибка: Файл конфигурации '{CONFIG_FILE}' не найден в текущей директории.")
        sys.exit(1)

    # Чтение и парсинг TOML
    try:
        with open(CONFIG_FILE, "rb") as f:
            config_data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Ошибка синтаксиса TOML в файле '{CONFIG_FILE}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка при чтению файла конфигурации: {e}")
        sys.exit(1)

    # Валидация параметров
    try:
        validated_config = validate_config(config_data)
    except ValueError as e:
        print("Ошибка валидации конфигурации:")
        print(e)
        sys.exit(1)

    # Вывод параметров в формате ключ-значение
    print("=== Успешно загруженная конфигурация прототипа ===")
    for key, value in validated_config.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
