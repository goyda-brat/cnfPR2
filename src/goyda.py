import configparser
import json
import os
import sys
import urllib.request

BIG_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GOOD_SYMBOLS = "abcdefghijklmnopqrstuvwxyz0123456789-_" + BIG_LETTERS
ONE = 1
TWO = 2
THREE = 3


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


def get_path(name):
    name = name.lower()
    if len(name) == ONE:
        return "1/" + name
    if len(name) == TWO:
        return "2/" + name
    if len(name) == THREE:
        return "3/" + name[0] + "/" + name
    return name[0:2] + "/" + name[2:4] + "/" + name


def download(url):
    try:
        answer = urllib.request.urlopen(url)
        return answer.read().decode("utf-8")
    except OSError:
        raise ValueError("не удалось скачать " + url)


def find_dependencies(text):
    last_version = None
    for line in text.splitlines():
        version = json.loads(line)
        if not version.get("yanked"):
            last_version = version
    if last_version is None:
        raise ValueError("у пакета нет доступных версий")
    names = []
    for dep in last_version["deps"]:
        if dep.get("kind") == "dev" or dep.get("kind") == "build":
            continue
        if dep.get("optional"):
            continue
        name = dep.get("package", dep["name"])
        if name not in names:
            names.append(name)
    names.sort()
    return names


def read_test_repo(path):
    graph = {}
    file = open(path, encoding="utf-8")
    for line in file:
        if ":" in line:
            parts = line.split(":")
            graph[parts[0].strip()] = parts[1].split()
    file.close()
    return graph


def get_dependencies(config):
    name = config["package_name"]
    if config["test_mode"] == "true":
        graph = read_test_repo(config["repository_url"])
        if name not in graph:
            raise ValueError("пакет " + name + " не найден в файле")
        return graph[name]
    url = config["repository_url"] + "/" + get_path(name)
    return find_dependencies(download(url))


def main(path):
    try:
        config = load_config(path)
        names = get_dependencies(config)
    except ValueError as error:
        print("Ошибка:", error)
        return
    print("Прямые зависимости пакета " + config["package_name"] + ":")
    if len(names) == 0:
        print("  нет зависимостей")
    for name in names:
        print("  " + name)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("config.ini")
