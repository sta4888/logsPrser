import json
import tempfile
import io

import pytest

from main import LogAnalyzer


def create_temp_log_file(lines):
    """Создаёт временный файл с JSON-логами."""
    tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8")
    for line in lines:
        tmp.write(json.dumps(line) + "\n")
    tmp.close()
    return tmp.name


def test_process_log_and_stats():
    """Проверяет, что process_log корректно собирает статистику по URL и времени ответа."""
    log_data = [
        {"url": "/api/context/...", "response_time": 0.024},
        {"url": "/api/specializations/...", "response_time": 0.016},
        {"url": "/api/context/...", "response_time": 0.032},
    ]
    file_path = create_temp_log_file(log_data)

    analyzer = LogAnalyzer([file_path], "average")

    analyzer.process_log()

    assert "/api/context/..." in analyzer.stats
    assert analyzer.stats["/api/context/..."]["count"] == 2
    assert abs(analyzer.stats["/api/context/..."]["total_time"] - 0.056) < 1e-9

    assert "/api/specializations/..." in analyzer.stats
    assert analyzer.stats["/api/specializations/..."]["count"] == 1
    assert analyzer.stats["/api/specializations/..."]["total_time"] == 0.016


def test_generate_average_report():
    """Проверяет, что generate_average_report возвращает корректные данные и среднее время."""
    analyzer = LogAnalyzer("fake_path", "average")
    analyzer.stats = {
        "/api/context/...": {"count": 2, "total_time": 0.056},
        "/api/specializations/...": {"count": 1, "total_time": 0.016},
    }

    report = analyzer.generate_average_report()

    assert len(report) == 2
    assert report[0][0] == "/api/context/..."
    assert abs(report[0][2] - 0.028) < 1e-9


def test_print_report_output(capsys):
    """Проверяет, что print_report выводит таблицу с корректными данными в stdout."""
    analyzer = LogAnalyzer("fake_path", "average")
    analyzer.stats = {
        "/api/context/...": {"count": 2, "total_time": 0.056},
        "/api/specializations/...": {"count": 1, "total_time": 0.016},
    }

    analyzer.print_report()
    captured = capsys.readouterr()

    assert "handler" in captured.out
    assert "/api/context/..." in captured.out
    assert "0.028000" in captured.out


def test_reader_handles_invalid_json(capsys):
    """Проверяет, что reader обрабатывает некорректный JSON и выводит сообщение об ошибке."""
    analyzer = LogAnalyzer("fake_path", "average")
    fake_file = io.StringIO('{"url": "/ok", "response_time": 0.1}\nINVALID_JSON\n')

    analyzer.reader(fake_file)
    captured = capsys.readouterr()

    assert "/ok" in analyzer.stats
    assert "Ошибка парсинга строки" in captured.out


def test_process_log_with_date_filter():
    """Проверяет, что date_filter фильтрует записи по указанной дате."""
    log_data = [
        {"@timestamp": "2025-06-22T13:57:34+00:00", "url": "/api/context/...", "response_time": 0.024},
        {"@timestamp": "2025-06-23T13:57:34+00:00", "url": "/api/context/...", "response_time": 0.032},
    ]
    file_path = create_temp_log_file(log_data)

    analyzer = LogAnalyzer([file_path], "average")
    analyzer.process_log(date_filter="2025-06-22")

    assert "/api/context/..." in analyzer.stats
    assert analyzer.stats["/api/context/..."]["count"] == 1
    assert abs(analyzer.stats["/api/context/..."]["total_time"] - 0.024) < 1e-9


def test_generate_average_report_sorting():
    """Проверяет, что generate_average_report сортирует результаты по количеству запросов."""
    analyzer = LogAnalyzer("fake_path", "average")
    analyzer.stats = {
        "/api/low": {"count": 1, "total_time": 0.01},
        "/api/high": {"count": 3, "total_time": 0.09},
    }

    report = analyzer.generate_average_report()
    assert report[0][0] == "/api/high"
    assert report[1][0] == "/api/low"


def test_print_report_invalid_type():
    """Проверяет, что print_report выбрасывает исключение при неизвестном типе отчёта."""
    analyzer = LogAnalyzer("fake_path", "unknown")
    with pytest.raises(ValueError) as excinfo:
        analyzer.print_report()
    assert "Неизвестный тип отчёта" in str(excinfo.value)


def test_empty_log_file(capsys):  # фикстура Pytest, перехвата вывод в stdout и stderr
    """Проверяет, что при пустом логе выводится только заголовок таблицы."""
    file_path = create_temp_log_file([])  # пустой лог
    analyzer = LogAnalyzer([file_path], "average")
    analyzer.process_log()
    analyzer.print_report()

    captured = capsys.readouterr()
    assert "handler" in captured.out
    assert "avg_response_time" in captured.out


def test_multiple_files_combined():
    """Проверяет, что статистика корректно суммируется при обработке нескольких файлов."""
    log1 = [
        {"url": "/api/context/...", "response_time": 0.01},
    ]
    log2 = [
        {"url": "/api/context/...", "response_time": 0.03},
    ]
    file1 = create_temp_log_file(log1)
    file2 = create_temp_log_file(log2)

    analyzer = LogAnalyzer([file1, file2], "average")
    analyzer.process_log()

    assert analyzer.stats["/api/context/..."]["count"] == 2
    assert abs(analyzer.stats["/api/context/..."]["total_time"] - 0.04) < 1e-9
