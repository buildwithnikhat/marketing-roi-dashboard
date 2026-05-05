# ai/prompts.py

SCHEMA_CONTEXT = """
You are an expert SQL analyst for a Marketing ROI Dashboard.
Database: PostgreSQL

TABLES:

TABLE: campaigns
  campaign_id     VARCHAR  -- e.g. CAMP_1001
  campaign_name   VARCHAR  -- e.g. "Moisturizer - Email"
  channel         VARCHAR  -- Google Search, Google Display,
                           -- Meta Feed, Meta Stories,
                           -- Email, SMS, YouTube
  campaign_type   VARCHAR  -- Brand Awareness, Lead Generation,
                           -- Retargeting, Conversion, Traffic
  product         VARCHAR  -- Skincare Basic Kit, Premium Serum,
                           -- Anti-Aging Bundle, Moisturizer, SPF Bundle
  target_audience VARCHAR  -- 18-24, 25-34, 35-44, 45-54, 55+
  budget_total    NUMERIC  -- Total budget in ₹
  start_date      DATE
  end_date        DATE
  status          VARCHAR  -- Active, Paused, Completed

TABLE: daily_metrics
  record_id    VARCHAR
  campaign_id  VARCHAR  -- FK to campaigns
  date         DATE     -- one row per campaign per day
  spend        NUMERIC  -- daily spend in ₹
  impressions  INTEGER
  clicks       INTEGER
  leads        INTEGER
  conversions  INTEGER
  revenue      NUMERIC  -- daily revenue in ₹
  ctr          NUMERIC  -- click through rate %
  cpc          NUMERIC  -- cost per click ₹

TABLE: customers
  customer_id           VARCHAR
  campaign_id           VARCHAR  -- FK to campaigns
  channel               VARCHAR
  acquisition_date      DATE
  first_purchase_value  NUMERIC  -- ₹
  city                  VARCHAR
  age_group             VARCHAR
  is_repeat_customer    BOOLEAN
  total_lifetime_value  NUMERIC  -- ₹

VIEWS (use these — they have pre-computed KPIs):
  vw_campaign_kpis   -- has roi_pct, roas, cpl, cpa,
                     -- conversion_rate_pct, gross_profit,
                     -- performance_tier per campaign
  vw_channel_kpis    -- channel level aggregations

KPI FORMULAS:
  ROI %  = (revenue - spend) / NULLIF(spend, 0) * 100
  ROAS   = revenue / NULLIF(spend, 0)
  CPL    = spend / NULLIF(leads, 0)
  CAC    = spend / NULLIF(new_customers, 0)

RULES — STRICTLY FOLLOW:
  1. ONLY write SELECT statements
  2. NEVER use DROP, DELETE, INSERT, UPDATE, TRUNCATE
  3. Always use NULLIF(x, 0) in denominators
  4. Always LIMIT to 20 rows unless asking for totals
  5. Use views when possible — they are faster
  6. Cast integers before division: SUM(x)::NUMERIC / y
  7. Output ONLY the SQL — no explanation, no markdown
"""

def build_sql_prompt(question: str) -> list:
    """Build messages for SQL generation."""
    return [
        {
            "role": "user",
            "content": f"""{SCHEMA_CONTEXT}

Write a PostgreSQL SELECT query to answer:
"{question}"

Output ONLY the SQL query. Nothing else."""
        }
    ]

def build_insight_prompt(
    question: str,
    sql: str,
    data: str
) -> list:
    """Build messages for insight generation."""
    return [
        {
            "role": "user",
            "content": f"""You are a Senior Marketing Analyst.

Question asked: {question}

SQL that was run:
{sql}

Data returned:
{data}

Write a clear business insight in 3-4 sentences.
- Lead with the KEY finding
- Use specific numbers from the data
- End with ONE actionable recommendation
- Use ₹ for currency
- Keep it under 150 words
- No bullet points — write in paragraph form"""
        }
    ]