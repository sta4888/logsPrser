import argparse

def parse_args():
    """
    Функция парсинга аргументов
    :return:
    """
    parser = argparse.ArgumentParser(description="Лог-анализатор")
    parser.add_argument("--file", required=True, help="Путь к лог-файлу")
    parser.add_argument("--report", choices=["average"], required=True, help="Тип отчёта")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(args)
