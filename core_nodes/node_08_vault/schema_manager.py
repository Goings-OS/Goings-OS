# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: AI-NATIVE SCHEMA INTERPRETER & OBSERVABILITY AGENT
# COMPLIANCE: ZERO EM-DASHES; DATABASE STABILITY MONITORING
# ==============================================================================

import os
import sys
import sqlite3
import re

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class SchemaManager:
    """Interprets markdown schema specifications and validates SQLite table structures."""

    def __init__(self, db_path: str, instructions_path: str):
        self.db_path = db_path
        self.instructions_path = instructions_path

    def parse_specifications(self) -> dict:
        """Parses schema specifications from instructions.md using regex matches."""
        schemas = {}
        if not os.path.exists(self.instructions_path):
            return schemas

        with open(self.instructions_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Match table definitions: '## Table: <name>'
        table_blocks = re.split(r"##\s+Table:\s+", content)[1:]
        for block in table_blocks:
            lines = block.strip().splitlines()
            if not lines:
                continue
            table_name = lines[0].strip()
            schemas[table_name] = {}
            for line in lines[1:]:
                if line.strip().startswith("-"):
                    parts = line.replace("-", "").strip().split(":")
                    if len(parts) >= 2:
                        col_name = parts[0].strip()
                        col_type = parts[1].strip().upper()
                        schemas[table_name][col_name] = col_type
        return schemas

    def detect_drift(self) -> dict:
        """Compares SQLite live database metadata against the target instructions schema."""
        drift_report = {
            "drift_detected": False,
            "missing_tables": [],
            "missing_columns": {},
            "type_mismatches": {}
        }

        target_schemas = self.parse_specifications()
        if not target_schemas:
            return drift_report

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for table_name, columns in target_schemas.items():
                cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if cursor.fetchone()[0] == 0:
                    drift_report["drift_detected"] = True
                    drift_report["missing_tables"].append(table_name)
                    continue

                cursor.execute(f"PRAGMA table_info({table_name})")
                live_columns = {row[1]: row[2].upper() for row in cursor.fetchall()}

                for col_name, col_type in columns.items():
                    if col_name not in live_columns:
                        drift_report["drift_detected"] = True
                        if table_name not in drift_report["missing_columns"]:
                            drift_report["missing_columns"][table_name] = []
                        drift_report["missing_columns"][table_name].append((col_name, col_type))
                    else:
                        # Normalize type check (e.g. TEXT UNIQUE or INTEGER PRIMARY KEY -> compare base types)
                        base_target = col_type.split()[0]
                        base_live = live_columns[col_name].split()[0]
                        if base_target != base_live:
                            drift_report["drift_detected"] = True
                            if table_name not in drift_report["type_mismatches"]:
                                drift_report["type_mismatches"][table_name] = []
                            drift_report["type_mismatches"][table_name].append((col_name, base_live, base_target))

            conn.close()
        except sqlite3.Error as err:
            drift_report["drift_detected"] = True
            drift_report["error"] = str(err)

        return drift_report


class DatabaseObservabilityAgent:
    """Monitors live database health metrics, WAL file sizes, and schema drifts."""

    def __init__(self, db_path: str, schema_manager: SchemaManager):
        self.db_path = db_path
        self.schema_manager = schema_manager

    def get_observability_metrics(self) -> dict:
        """Gathers database metrics, checking file locks and integrity checks."""
        metrics = {
            "db_active": False,
            "db_size_bytes": 0,
            "wal_size_bytes": 0,
            "integrity_pass": False,
            "drift_status": {}
        }

        if not os.path.exists(self.db_path):
            return metrics

        metrics["db_size_bytes"] = os.path.getsize(self.db_path)
        wal_path = f"{self.db_path}-wal"
        if os.path.exists(wal_path):
            metrics["wal_size_bytes"] = os.path.getsize(wal_path)

        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()[0]
            metrics["integrity_pass"] = (res == "ok")
            metrics["db_active"] = True
            conn.close()
        except sqlite3.Error:
            metrics["integrity_pass"] = False

        metrics["drift_status"] = self.schema_manager.detect_drift()
        return metrics
