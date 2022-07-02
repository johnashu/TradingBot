import json, csv, os


def open_file(fn: str) -> list:
    with open(fn, "r") as f:
        return f.read()


def open_json(fn: str) -> dict:
    with open(fn, "r", encoding="utf-8") as j:
        return json.load(j)


def save_json(fn: str, d: dict):
    with open(f"{fn}.json", "w", encoding="utf-8") as j:
        return json.dump(d, j, indent=4)


def open_csv(fn: str) -> dict:
    with open(fn, "r", newline="", encoding="utf-8") as csvfile:
        r = csv.DictReader(csvfile, delimiter=",")
        return list(r)


def create_data_path(pth: str, data_path: str = "data") -> os.path:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path, pth)
    if not os.path.exists(p):
        os.mkdir(p)
    return p
