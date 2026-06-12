"""Export a legacy Cerebrum RethinkDB schema into the simulator snapshot format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rethinkdb import r


LEGACY_TABLES = (
    "hearing_timestamps",
    "vision_timestamps",
    "language_timestamps",
    "crossmodal_mappings",
)


def export_snapshot(host: str, port: int, database: str, output: Path) -> None:
    conn = r.connect(host, port)
    try:
        payload = {}
        for table in LEGACY_TABLES:
            try:
                rows = list(r.db(database).table(table).run(conn))
            except Exception:
                rows = []
            payload[table] = rows
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=28015)
    parser.add_argument("--database", default="test")
    parser.add_argument(
        "--output",
        default="examples/legacy_cerebrum_snapshot.from_rethinkdb.json",
        help="Path to the exported snapshot JSON file.",
    )
    args = parser.parse_args()
    export_snapshot(args.host, args.port, args.database, Path(args.output))


if __name__ == "__main__":
    main()
