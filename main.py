import argparse
import csv
import json
from collections import defaultdict
from typing import Any


def parse_args():
    """Парсинг аргументов"""
    parser = argparse.ArgumentParser(description="Лог-анализатор")
    parser.add_argument(
        "--files",
        required=True,
        nargs="+",  # принимает один или несколько файлов
        help="Пути к лог-файлам"
    )
    parser.add_argument(
        "--report",
        choices=["average"],
        required=True,
        help="Тип отчёта"
    )
    return parser.parse_args()



class LogAnalyzer:
    def __init__(self, file_path, report_type):
        self.file_path = file_path
        self.report_type = report_type
        self.stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

    def process_log(self):
        """Чтение всех лог-файлов и сбор статистики"""
        for file_path in self.file_path:  # теперь self.file_path — список
            with open(file_path, "r", encoding="utf-8") as f:
                self.reader(f)

    def reader(self, f):
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                url = data.get("url")
                response_time = float(data.get("response_time", 0))
                self.stats[url]["count"] += 1
                self.stats[url]["total_time"] += response_time
            except json.JSONDecodeError:
                print(f"Ошибка парсинга строки: {line}")


    def generate_average_report(self) -> list[Any]:
        """Формирование отчета: URL, количество запросов, среднее время"""
        report = []
        for url, values in self.stats.items():
            avg_time = values["total_time"] / values["count"]
            report.append((url, values["count"], avg_time))
        report.sort(key=lambda x: x[1], reverse=True)
        return report

    def print_report(self):
        """Вывод отчета в консоль"""
        if self.report_type == "average":
            report = self.generate_average_report()
            print(f"{' ' * 3} {'handler':<40} {'total':<10} {'avg_response_time':<20}")
            print("-" * 3, "-" * 40, "-" * 10, "-" * 20)
            for num, data in enumerate(report):
                print(f"{num:<3}  {data[0]:<40} {data[1]:<10} {data[2]:<20.6f}")





def main():
    args = parse_args()
    analyzer = LogAnalyzer(args.files, args.report)  # передаём список
    analyzer.process_log()
    analyzer.print_report()



if __name__ == "__main__":
    main()
