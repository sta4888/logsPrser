import argparse
import json
from collections import defaultdict

def parse_args():
    """
    Функция парсинга аргументов
    :return:
    """
    parser = argparse.ArgumentParser(description="Лог-анализатор")
    parser.add_argument("--file", required=True, help="Путь к лог-файлу")
    parser.add_argument("--report", choices=["average"], required=True, help="Тип отчёта")
    return parser.parse_args()

def process_log(file_path):
    stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                url = data.get("url")
                response_time = float(data.get("response_time", 0))
                stats[url]["count"] += 1
                stats[url]["total_time"] += response_time
            except json.JSONDecodeError:
                print(f"Ошибка парсинга строки: {line}")

    return stats

def generate_average_report(stats):
    report = []
    for url, values in stats.items():
        avg_time = values["total_time"] / values["count"]
        report.append((url, values["count"], avg_time))
    report.sort(key=lambda x: x[1], reverse=True)
    return report

def main():
    args = parse_args()
    stats = process_log(args.file)

    if args.report == "average":
        report = generate_average_report(stats)
        print(f"{'URL':<40} {'Requests':<10} {'Avg Response Time (s)':<20}")
        print("-" * 70)
        for url, count, avg_time in report:
            print(f"{url:<40} {count:<10} {avg_time:<20.6f}")

if __name__ == "__main__":
    main()
