import argparse
import json
import re
from tabulate import tabulate

handle_dict, total_dict, data_dict = {}, {}, {}


def main():
    parser_json = [(_["url"], _["response_time"], _["@timestamp"],
                    _["http_user_agent"]) for _ in parse_json_files(get_pars_args().file)]

    for elem in parser_json:
        url, response_time, timestamp, user_agent = elem

        if url in handle_dict:
            handle_dict[url] += response_time
            total_dict[url] += 1
        else:
            handle_dict[url] = response_time
            total_dict[url] = 1
            data_dict[url] = timestamp

    if get_pars_args().report == "average":
        print(tabulate(get_average(total_dict), headers=["handler", "res_time", "total"], tablefmt="github"))
    elif get_pars_args().report == "data":
        print(tabulate(get_data(data_dict), headers=["handler", "res_time"], tablefmt="github"))


def get_pars_args():
    parser = argparse.ArgumentParser(description="Script Parser for Command Line Arguments")
    parser.add_argument("--file", type=argparse.FileType('r'), help="name file", nargs=2, required=True)
    parser.add_argument("--report", choices=["average", "data"], default="",
                        help="average: количество ссылок, data: весь список", required=True)
    return parser.parse_args()


def get_average(total_dicts):
    return [(key, round(value / int(total_dicts[key]), 3), total_dicts[key]) for key, value in handle_dict.items()]


def get_data(data_dicts):
    input_data = input("Введите дату в формате YYYY-MM-DD: ")
    return [(k, v) for k, v in data_dicts.items() if isinstance(v, str) and re.match(rf"^{input_data}.*", v)]


def parse_json_files(files):
    combined_json = []
    for file in files:
        for line in file:
            try:
                combined_json.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return combined_json


if __name__ == "__main__":
    main()
