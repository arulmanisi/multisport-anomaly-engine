"""Lightweight persistence for anomaly results using SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List

from cae.data.schemas import AnomalyResult

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS anomaly_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL,
    over INTEGER NOT NULL,
    ball INTEGER NOT NULL,
    anomaly_score REAL NOT NULL,
    is_anomaly INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class ResultStore:
    """Store anomaly results in a local SQLite database."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._memory_conn: sqlite3.Connection | None = None
        if str(self.db_path) == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        if self._memory_conn:
            return self._memory_conn
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        conn = self._connect()
        conn.executescript(SCHEMA_SQL)
        conn.commit()

    def save_results(self, results: Iterable[AnomalyResult]) -> None:
        rows = [
            (
                result.match_id,
                result.over,
                result.ball,
                result.anomaly_score,
                int(result.is_anomaly),
                result.reason,
            )
            for result in results
        ]
        if not rows:
            return
        conn = self._connect()
        conn.executemany(
            """
            INSERT INTO anomaly_results
            (match_id, over, ball, anomaly_score, is_anomaly, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
        if self._memory_conn is None:
            conn.close()

    def fetch_recent(self, limit: int = 50) -> List[AnomalyResult]:
        conn = self._connect()
        cursor = conn.execute(
            """
            SELECT match_id, over, ball, anomaly_score, is_anomaly, reason
            FROM anomaly_results
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        if self._memory_conn is None:
            conn.close()
        results: List[AnomalyResult] = []
        for row in rows:
            match_id, over, ball, anomaly_score, is_anomaly, reason = row
            results.append(
                AnomalyResult(
                    match_id=match_id,
                    over=int(over),
                    ball=int(ball),
                    anomaly_score=float(anomaly_score),
                    is_anomaly=bool(is_anomaly),
                    reason=reason,
                )
            )
        return results
