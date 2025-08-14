import json
import tempfile
import io
from main import LogAnalyzer


def create_temp_log_file(lines):
    """Создаёт временный файл с JSON-логами"""
    tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8")
    for line in lines:
        tmp.write(json.dumps(line) + "\n")
    tmp.close()
    return tmp.name


def test_process_log_and_stats():
    # Arrange
    log_data = [
        {"url": "/api/context/...", "response_time": 0.024},
        {"url": "/api/specializations/...", "response_time": 0.016},
        {"url": "/api/context/...", "response_time": 0.032},
    ]
    file_path = create_temp_log_file(log_data)

    analyzer = LogAnalyzer([file_path], "average")

    # Act
    analyzer.process_log()

    # Assert
    assert "/api/context/..." in analyzer.stats
    assert analyzer.stats["/api/context/..."]["count"] == 2
    assert abs(analyzer.stats["/api/context/..."]["total_time"] - 0.056) < 1e-9

    assert "/api/specializations/..." in analyzer.stats
    assert analyzer.stats["/api/specializations/..."]["count"] == 1
    assert analyzer.stats["/api/specializations/..."]["total_time"] == 0.016


def test_generate_average_report():
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
    analyzer = LogAnalyzer("fake_path", "average")
    analyzer.stats = {
        "/api/context/...": {"count": 2, "total_time": 0.056},
        "/api/specializations/...": {"count": 1, "total_time": 0.016},
    }

    analyzer.print_report()
    captured = capsys.readouterr()

    assert "handler" in captured.out
    assert "/api/context/..." in captured.out
    assert "0.028000" in captured.out  # среднее время


def test_reader_handles_invalid_json(capsys):
    analyzer = LogAnalyzer("fake_path", "average")
    fake_file = io.StringIO('{"url": "/ok", "response_time": 0.1}\nINVALID_JSON\n')

    analyzer.reader(fake_file)
    captured = capsys.readouterr()

    assert "/ok" in analyzer.stats
    assert "Ошибка парсинга строки" in captured.out
