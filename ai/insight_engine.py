# ai/insight_engine.py

import anthropic
import os
import re
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

from ai.sql_validator import SQLValidator
from ai.sql_executor  import SQLExecutor
from ai.prompts       import build_sql_prompt, build_insight_prompt

load_dotenv()

@dataclass
class InsightResult:
    question:      str
    sql_generated: Optional[str] = None
    answer:        Optional[str] = None
    data_rows:     int = 0
    success:       bool = False
    error:         Optional[str] = None
    time_ms:       float = 0


class InsightEngine:
    """
    Full pipeline:
    Question → SQL → Validate → Execute → Insight
    """

    def __init__(self):
        self.client    = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.validator = SQLValidator()
        self.executor  = SQLExecutor()
        self.model     = "claude-sonnet-4-20250514"

    def _call_claude(self, messages: list,
                     max_tokens: int = 500,
                     temperature: float = 0) -> str:
        """Make one Claude API call."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages
        )
        return response.content[0].text.strip()

    def _clean_sql(self, raw: str) -> str:
        """Strip markdown from SQL output."""
        sql = re.sub(r'```sql\s*', '', raw, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*', '', sql)
        sql = sql.strip()
        if not sql.endswith(';'):
            sql += ';'
        return sql

    def run(self, question: str) -> InsightResult:
        """Run the full pipeline."""
        import time
        start  = time.time()
        result = InsightResult(question=question)

        try:
            # ── STEP 1: Generate SQL ──────────────────
            print(f"\n🤖 Question: {question}")
            print("   Step 1: Generating SQL...")

            messages = build_sql_prompt(question)
            raw_sql  = self._call_claude(
                messages, max_tokens=400, temperature=0
            )
            sql = self._clean_sql(raw_sql)
            result.sql_generated = sql
            print(f"   SQL: {sql[:80]}...")

            # ── STEP 2: Validate SQL ──────────────────
            print("   Step 2: Validating...")
            is_safe, error = self.validator.validate(sql)

            if not is_safe:
                result.error = f"Safety check failed: {error}"
                print(f"   ❌ {result.error}")
                return result

            print("   ✅ SQL is safe")

            # ── STEP 3: Execute SQL ───────────────────
            print("   Step 3: Executing...")
            df, exec_ms, error = self.executor.execute(sql)

            if error:
                # Try self-healing
                print(f"   ⚠️  Error: {error}. Trying to fix...")
                sql = self._self_heal(question, sql, error)
                if sql:
                    result.sql_generated = sql
                    df, exec_ms, error = self.executor.execute(sql)

            if error:
                result.error = f"Query failed: {error}"
                return result

            result.data_rows = len(df)
            print(f"   ✅ Got {len(df)} rows in {exec_ms}ms")

            if df.empty:
                result.answer  = (
                    "No data found for that question. "
                    "Try rephrasing or check the date range."
                )
                result.success = True
                return result

            # ── STEP 4: Generate Insight ──────────────
            print("   Step 4: Generating insight...")
            data_str = self.executor.to_context_string(df)

            insight_messages = build_insight_prompt(
                question=question,
                sql=sql,
                data=data_str
            )
            answer = self._call_claude(
                insight_messages,
                max_tokens=300,
                temperature=0
            )

            result.answer  = answer
            result.success = True
            result.time_ms = round(
                (time.time()-start)*1000, 2
            )
            print(f"   ✅ Done in {result.time_ms}ms")

            return result

        except anthropic.APIError as e:
            result.error = f"AI API error: {str(e)}"
            return result
        except Exception as e:
            result.error = f"Error: {str(e)}"
            return result

    def _self_heal(self, question: str,
                   failed_sql: str,
                   error: str) -> Optional[str]:
        """Ask Claude to fix broken SQL."""
        messages = [{
            "role": "user",
            "content": (
                f"Fix this PostgreSQL query.\n"
                f"Question: {question}\n"
                f"Broken SQL: {failed_sql}\n"
                f"Error: {error}\n"
                f"Output ONLY the fixed SQL. Nothing else."
            )
        }]
        try:
            raw = self._call_claude(
                messages, max_tokens=400, temperature=0
            )
            return self._clean_sql(raw)
        except Exception:
            return None