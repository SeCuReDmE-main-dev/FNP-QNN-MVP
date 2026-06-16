from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


class GlymphaticScanTests(unittest.TestCase):
    def test_scan_writes_report_and_tags_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache_dir = root / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "module.pyc").write_bytes(b"abc")

            big_log = root / "big.log"
            big_log.write_bytes(b"\0" * (1024 * 1024 + 32))

            old_report = root / "reports" / "glymphatic" / "old.json"
            old_report.parent.mkdir(parents=True)
            old_report.write_text("{}", encoding="utf-8")
            old_time = time.time() - (31 * 24 * 60 * 60)
            os.utime(old_report, (old_time, old_time))

            quantum_session = root / "qiskit_session_demo.json"
            quantum_session.write_text("{}", encoding="utf-8")
            torch_worker = root / "torch_worker_demo.pid"
            torch_worker.write_text("1234", encoding="utf-8")

            before_files = {path.relative_to(root).as_posix() for path in root.rglob("*")}
            result = subprocess.run(
                [sys.executable, "-m", "scripts.glymphatic_scan", "--root", str(root)],
                cwd=Path(__file__).resolve().parent.parent,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_files = list((root / "reports" / "glymphatic").glob("scan-*.json"))
            self.assertEqual(len(report_files), 1)

            report = json.loads(report_files[0].read_text(encoding="utf-8"))
            items = {item["path"]: item for item in report["items"]}

            self.assertEqual(items["__pycache__"]["tag"], "safe-to-close")
            self.assertEqual(items["__pycache__"]["kind"], "cache_dir")
            self.assertEqual(items["big.log"]["tag"], "safe-to-close")
            self.assertEqual(items["big.log"]["kind"], "log_file")
            self.assertEqual(items["reports/glymphatic/old.json"]["tag"], "confirm-required")
            self.assertEqual(items["reports/glymphatic/old.json"]["kind"], "old_report")
            self.assertEqual(items["qiskit_session_demo.json"]["tag"], "human-only")
            self.assertEqual(items["qiskit_session_demo.json"]["kind"], "quantum_session")
            self.assertEqual(items["torch_worker_demo.pid"]["tag"], "human-only")
            self.assertEqual(items["torch_worker_demo.pid"]["kind"], "torch_worker")

            after_files = {path.relative_to(root).as_posix() for path in root.rglob("*")}
            self.assertTrue(before_files.issubset(after_files))
            self.assertIn("No process killed. No file deleted. No network call.", report["notes"][0])
