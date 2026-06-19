import csv
import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_technicians() -> List[Dict]:
    path = DATA_DIR / "technicians.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_category_durations() -> Dict[str, float]:
    path = DATA_DIR / "category_durations.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_training_data() -> List[Dict[str, str]]:
    path = DATA_DIR / "training_data.csv"
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_decision_logs() -> List[Dict]:
    path = DATA_DIR / "decision_logs.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_decision_log(entry: Dict) -> None:
    path = DATA_DIR / "decision_logs.json"
    logs = load_decision_logs()
    logs.append(entry)
    with path.open("w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
