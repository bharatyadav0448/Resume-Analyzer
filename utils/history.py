import json
import os


HISTORY_FILE = "analysis_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history_entry(entry):
    history = load_history()
    history.insert(0, entry)

    with open(HISTORY_FILE, "w") as file:
        json.dump(history[:50], file, indent=2)
