# ai/sql_validator.py

import re


class SQLValidator:
    """Validates AI-generated SQL before execution."""

    FORBIDDEN = [
        r'\bDROP\b',     r'\bDELETE\b',
        r'\bINSERT\b',   r'\bUPDATE\b',
        r'\bTRUNCATE\b', r'\bALTER\b',
        r'\bCREATE\b',   r'\bGRANT\b',
        r'\bEXEC\b',     r'\bpg_user\b',
        r'\bpg_shadow\b',
    ]

    def validate(self, sql: str) -> tuple:
        """Returns (is_safe, error_message)"""
        if not sql or not sql.strip():
            return False, "Empty SQL"

        sql_upper = sql.upper().strip()

        if not (sql_upper.startswith('SELECT') or
                sql_upper.startswith('WITH')):
            return False, f"Must be SELECT. Got: {sql[:30]}"

        for pattern in self.FORBIDDEN:
            if re.search(pattern, sql_upper):
                return False, f"Forbidden: {pattern}"

        statements = [s.strip() for s in sql.split(';')
                      if s.strip()]
        if len(statements) > 1:
            return False, "Multiple statements not allowed"

        return True, None