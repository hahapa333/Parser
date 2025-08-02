import pytest
from parser import script_parser
import sys


@pytest.fixture
def sample_data():
    return [
        {"url": "http://example.com/api", "response_time": 0.123, "@timestamp": "2023-10-01T12:00:00Z",
         "http_user_agent": "TestAgent/1.0"},
        {"url": "http://example.com/api", "response_time": 0.456, "@timestamp": "2023-10-01T12:01:00Z",
         "http_user_agent": "TestAgent/1.0"},
        {"url": "http://example.com/other", "response_time": 0.789, "@timestamp": "2023-10-01T12:02:00Z",
         "http_user_agent": "TestAgent/1.0"}
    ]


def test_handle_dict(sample_data):
    for entry in sample_data:
        url = entry["url"]
        response_time = entry["response_time"]

        if url in script_parser.handle_dict:
            script_parser.handle_dict[url] += response_time
        else:
            script_parser.handle_dict[url] = response_time

    # Check if the handle_dict is populated correctly
    assert script_parser.handle_dict["http://example.com/api"] == 0.579  # 0.123 + 0.456
    assert script_parser.handle_dict["http://example.com/other"] == 0.789
    assert len(script_parser.handle_dict) == 2  # Two unique URLs processed


def test_total_dict(sample_data):
    for entry in sample_data:
        url = entry["url"]

        if url in script_parser.total_dict:
            script_parser.total_dict[url] += 1
        else:
            script_parser.total_dict[url] = 1

    assert script_parser.total_dict["http://example.com/api"] == 2  # Two entries for this URL
    assert script_parser.total_dict["http://example.com/other"] == 1  # One entry for this URL
    assert len(script_parser.total_dict) == 2  # Two unique URLs processe


def test_data_dict(sample_data):
    for entry in sample_data:
        url = entry["url"]
        timestamp = entry["@timestamp"]

        if url in script_parser.data_dict:
            script_parser.data_dict[url] += f", {timestamp}"
        else:
            script_parser.data_dict[url] = timestamp

    # Check if the data_dict is populated correctly
    assert script_parser.data_dict["http://example.com/api"] == "2023-10-01T12:00:00Z, 2023-10-01T12:01:00Z"
    assert script_parser.data_dict["http://example.com/other"] == "2023-10-01T12:02:00Z"
    assert len(script_parser.data_dict) == 2  # Two unique URLs processed


def test_get_data(monkeypatch):
    data_dict = {
        "/test/url": "2023-10-01T10:00:00Z",
        "/other/url": "2025-07-30T10:00:00Z"
    }

    monkeypatch.setattr("builtins.input", lambda _: "2023-10-01")

    result = script_parser.get_data(data_dict)
    assert result == [("/test/url", "2023-10-01T10:00:00Z")]


def test_get_average():
    total_dict = {
        "http://example.com/api": 2,
        "http://example.com/other": 1
    }
    script_parser.handle_dict = {
        "http://example.com/api": 0.579,
        "http://example.com/other": 0.789
    }

    result = script_parser.get_average(total_dict)
    assert result == [
        ("http://example.com/api", 0.289, 2),
        ("http://example.com/other", 0.789, 1)
    ]

# Имитируем чтение из файла JSON для тестирования функции parse_json_files
def test_parse_json_files(monkeypatch):
    # Mock the file input
    mock_file = [
        "{\"url\": \"http://example.com/api\", \"response_time\": 0.123, \"@timestamp\": \"2023-10-01T12:00:00Z\", \"http_user_agent\": \"TestAgent/1.0\"}\n",
        "{\"url\": \"http://example.com/other\", \"response_time\": 0.456, \"@timestamp\": \"2023-10-01T12:01:00Z\", \"http_user_agent\": \"TestAgent/1.0\"}\n"]

    monkeypatch.setattr("builtins.open", lambda f, mode='r': mock_file)

    result = script_parser.parse_json_files([mock_file])
    assert len(result) == 2
    assert result[0]["url"] == "http://example.com/api"
    assert result[1]["url"] == "http://example.com/other"


# Имитируем аргументы командной строки для тестирования функции get_pars_args
def test_argparse_parsing(monkeypatch):
    test_args = ["script_parser.py", "--report", "average", "--file", "total.log", "example2.log"]
    monkeypatch.setattr(sys, "argv", test_args)

    args = script_parser.get_pars_args()

    assert args.report == "average"
    assert [f.name for f in args.file] == ["total.log", "example2.log"]

