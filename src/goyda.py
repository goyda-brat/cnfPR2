# Запуск: python3 src/stage1.py config.ini
import configparser
import os
import sys

CAPITALS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
NAME_SYMBOLS = "abcdefghijklmnopqrstuvwxyz" + CAPITALS + DIGITS + "-_"

def read_config(path):
    if not os.path.isfile(path):
        raise ValueError("файл конфигурации не найден: " + path)
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        raise ValueError("неверный формат INI-файла")
    if not parser.has_section("depgraph"):
        raise ValueError("в файле нет секции [depgraph]")
    return parser["depgraph"]


def get_value(section, key):
    value = section.get(key, "").strip()
    if value == "":
        raise ValueError("не задан параметр " + key)
    return value


def check_test_values(package, repository):
    for letter in package:
        if letter not in CAPITALS:
            raise ValueError("в тестовом режиме имя пакета - большие буквы")
    if not os.path.isfile(repository):
        raise ValueError("файл тестового репозитория не найден")


def check_real_values(package, repository): #проверить имя пакета и адрес реп
    if package[0] in DIGITS + "-_":
        raise ValueError("имя пакета должно начинаться с буквы")
    for letter in package:
        if letter not in NAME_SYMBOLS:
            raise ValueError("неверное имя пакета: " + package)
    if not repository.startswith(("http://", "https://")):
        raise ValueError("адрес репозитория должен начинаться с http(s)://")


def check_config(section): #вернуть в виде словаря
    package = get_value(section, "package_name")
    repository = get_value(section, "repository_url")
    mode = get_value(section, "test_mode")
    text = section.get("filter_substring", "").strip()
    if mode not in ("true", "false"):
        raise ValueError("test_mode должен быть true или false")
    if " " in text:
        raise ValueError("filter_substring не должен содержать пробелов")
    if mode == "true":
        check_test_values(package, repository)
    else:
        check_real_values(package, repository)
    return {
        "package_name": package,
        "repository_url": repository,
        "test_mode": mode,
        "filter_substring": text,
    }


def print_config(config): #ключ-значение
    for key in config:
        print(key, "=", config[key])


def main(path):
    try:
        config = check_config(read_config(path))
    except ValueError as error:
        print("Ошибка:", error, file=sys.stderr)
        return 2
    print_config(config)
    return 0


if __name__ == "__main__":
    config_path = "config.ini"
    if sys.argv[1:]:
        config_path = sys.argv[1]
    sys.exit(main(config_path))