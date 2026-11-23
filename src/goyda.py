import configparser
import os
import sys

BIG_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GOOD_SYMBOLS = "abcdefghijklmnopqrstuvwxyz0123456789-_" + BIG_LETTERS


def read_config(path):
    if not os.path.isfile(path):
        raise ValueError("файл конфигурации не найден: " + path)
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        raise ValueError("неверный формат INI-файла")
    if "depgraph" not in parser:
        raise ValueError("в файле нет секции [depgraph]")
    return parser["depgraph"]


def get_value(section, key):
    value = section.get(key, "").strip()
    if value == "":
        raise ValueError("не задан параметр " + key)
    return value


def check_name(name, test_mode):
    for letter in name:
        if test_mode == "true" and letter not in BIG_LETTERS:
            raise ValueError("в тестовом режиме имя пакета - большие буквы")
        if letter not in GOOD_SYMBOLS:
            raise ValueError("неверное имя пакета: " + name)


def check_repository(repository, test_mode):
    if test_mode == "true":
        if not os.path.isfile(repository):
            raise ValueError("файл тестового репозитория не найден")
    elif not repository.startswith("http"):
        raise ValueError("адрес репозитория должен начинаться с http")


def load_config(path):
    section = read_config(path)
    config = {}
    config["package_name"] = get_value(section, "package_name")
    config["repository_url"] = get_value(section, "repository_url")
    config["test_mode"] = get_value(section, "test_mode")
    config["filter_substring"] = section.get("filter_substring", "").strip()
    if config["test_mode"] != "true" and config["test_mode"] != "false":
        raise ValueError("test_mode должен быть true или false")
    if " " in config["filter_substring"]:
        raise ValueError("filter_substring не должен содержать пробелов")
    check_name(config["package_name"], config["test_mode"])
    check_repository(config["repository_url"], config["test_mode"])
    return config


def main(path):
    try:
        config = load_config(path)
    except ValueError as error:
        print("Ошибка:", error)
        return
    for key in config:
        print(key, "=", config[key])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("config.ini")
