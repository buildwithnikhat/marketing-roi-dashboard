# ai/sql_executor.py

import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import time

load_dotenv()

class SQLExecutor:
    """Executes validated SQL safely."""

    MAX_ROWS      = 100
    TIMEOUT_SECS  = 15

    def __init__(self):
        db_url = (
            f"postgresql://{os.getenv('DB_USER','postgres')}:"
            f"{os.getenv('DB_PASSWORD','1410')}@"
            f"{os.getenv('DB_HOST','localhost')}:"
            f"{os.getenv('DB_PORT',5432)}/"
            f"{os.getenv('DB_NAME','marketing_roi_db')}"
        )
        self.engine = create_engine(
            db_url,
            connect_args={
                "options": f"-c statement_timeout="
                           f"{self.TIMEOUT_SECS * 1000}"
            }
        )

    def execute(self, sql: str) -> tuple:
        """
        Execute SQL → returns (DataFrame, time_ms, error)
        Never raises — always returns error string instead.
        """
        start = time.time()
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)

            ms = round((time.time()-start)*1000, 2)

            # Limit rows
            if len(df) > self.MAX_ROWS:
                df = df.head(self.MAX_ROWS)

            return df, ms, None

        except Exception as e:
            ms = round((time.time()-start)*1000, 2)
            return pd.DataFrame(), ms, str(e)

    def to_context_string(self, df: pd.DataFrame,
                           max_rows: int = 15) -> str:
        """Convert DataFrame to string for AI context."""
        if df.empty:
            return "Query returned no results."

        lines = []
        lines.append(f"Total rows: {len(df)}")
        lines.append(f"Columns: {', '.join(df.columns)}")
        lines.append("")
        lines.append(df.head(max_rows).to_string(index=False))

        # Add numeric summary
        num_cols = df.select_dtypes(include='number').columns
        if len(num_cols) > 0:
            lines.append("\nSummary stats:")
            lines.append(
                df[num_cols].describe().round(2).to_string()
            )

        return "\n".join(lines)