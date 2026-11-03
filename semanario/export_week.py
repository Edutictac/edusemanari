"""Exporta los mensajes de una semana para preparar el borrador editorial."""

import argparse
import json
from datetime import date, timedelta

from .storage import connect, load_config, week_messages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--week", required=True, help="Lunes de la semana: AAAA-MM-DD")
    args = parser.parse_args()
    monday = date.fromisoformat(args.week)
    config = load_config(args.config)
    db = connect(config["database"])
    data = {
        "week_start": monday.isoformat(),
        "week_end": (monday + timedelta(days=6)).isoformat(),
        "messages": week_messages(db, monday, config["timezone"]),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
