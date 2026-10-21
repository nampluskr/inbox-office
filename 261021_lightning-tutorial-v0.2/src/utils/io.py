import json
import os


def save_json(path, values):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(values, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")
