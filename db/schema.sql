-- db/schema.sql
-- Marketing ROI Dashboard — Complete Database Schema

-- ─────────────────────────────────────────────────────
-- TABLE 1: campaigns
-- Master table — one row per campaign
-- ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id       VARCHAR(20)     PRIMARY KEY,
    campaign_name     VARCHAR(255)    NOT NULL,
    channel           VARCHAR(50)     NOT NULL,
    campaign_type     VARCHAR(50),
    product           VARCHAR(100),
    target_audience   VARCHAR(20),
    budget_total      NUMERIC(12,2)   NOT NULL CHECK (budget_total > 0),
    start_date        DATE            NOT NULL,
    end_date          DATE            NOT NULL,
    status            VARCHAR(20)     DEFAULT 'Active',
    duration_days     INTEGER,
    created_by        VARCHAR(100)    DEFAULT 'system',
    created_at        TIMESTAMP       DEFAULT NOW(),
    updated_at        TIMESTAMP       DEFAULT NOW(),
    CONSTRAINT valid_dates CHECK (end_date >= start_date)
);

-- ─────────────────────────────────────────────────────
-- TABLE 2: daily_metrics
-- Fact table — one row per campaign per day
-- This is where ALL KPIs come from
-- ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS daily_metrics (
    record_id       VARCHAR(20)     PRIMARY KEY,
    campaign_id     VARCHAR(20)     NOT NULL,
    date            DATE            NOT NULL,
    spend           NUMERIC(12,2)   NOT NULL CHECK (spend >= 0),
    impressions     INTEGER         NOT NULL CHECK (impressions >= 0),
    clicks          INTEGER         NOT NULL CHECK (clicks >= 0),
    leads           INTEGER         DEFAULT 0 CHECK (leads >= 0),
    conversions     INTEGER         DEFAULT 0 CHECK (conversions >= 0),
    revenue         NUMERIC(14,2)   DEFAULT 0 CHECK (revenue >= 0),
    ctr             NUMERIC(8,4),
    cpc             NUMERIC(10,2),
    data_source     VARCHAR(50)     DEFAULT 'synthetic',
    ingested_at     TIMESTAMP       DEFAULT NOW(),

    -- Foreign key links to campaigns table
    CONSTRAINT fk_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id)
        ON DELETE RESTRICT,

    -- One record per campaign per day only
    CONSTRAINT unique_campaign_date
        UNIQUE (campaign_id, date),

    -- Logical constraints
    CONSTRAINT clicks_lte_impressions
        CHECK (clicks <= impressions),
    CONSTRAINT conversions_lte_clicks
        CHECK (conversions <= clicks)
);

-- ─────────────────────────────────────────────────────
-- TABLE 3: customers
-- One row per acquired customer
-- Used for CAC calculations
-- ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS customers (
    customer_id           VARCHAR(20)   PRIMARY KEY,
    campaign_id           VARCHAR(20)   NOT NULL,
    channel               VARCHAR(50)   NOT NULL,
    acquisition_date      DATE          NOT NULL,
    first_purchase_value  NUMERIC(10,2) CHECK (first_purchase_value >= 0),
    email                 VARCHAR(255),
    city                  VARCHAR(100),
    age_group             VARCHAR(20),
    is_repeat_customer    BOOLEAN       DEFAULT FALSE,
    total_lifetime_value  NUMERIC(12,2) DEFAULT 0,
    total_orders          INTEGER       DEFAULT 1,
    created_at            TIMESTAMP     DEFAULT NOW(),

    CONSTRAINT fk_customer_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id)
        ON DELETE RESTRICT
);

-- ─────────────────────────────────────────────────────
-- TABLE 4: kaggle_customers
-- Stores the cleaned Kaggle marketing data
-- Used for customer behaviour analysis
-- ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS kaggle_customers (
    id                        INTEGER       PRIMARY KEY,
    year_birth                INTEGER,
    age                       INTEGER,
    age_group                 VARCHAR(20),
    education                 VARCHAR(50),
    marital_status            VARCHAR(20),
    income                    NUMERIC(12,2),
    kidhome                   INTEGER,
    teenhome                  INTEGER,
    dt_customer               DATE,
    tenure_days               INTEGER,
    tenure_years              NUMERIC(5,1),
    recency                   INTEGER,
    total_spending            NUMERIC(12,2),
    mnt_wines                 NUMERIC(10,2),
    mnt_fruits                NUMERIC(10,2),
    mnt_meat_products         NUMERIC(10,2),
    mnt_fish_products         NUMERIC(10,2),
    mnt_sweet_products        NUMERIC(10,2),
    mnt_gold_prods            NUMERIC(10,2),
    num_deals_purchases       INTEGER,
    num_web_purchases         INTEGER,
    num_catalog_purchases     INTEGER,
    num_store_purchases       INTEGER,
    num_web_visits_month      INTEGER,
    total_campaigns_accepted  INTEGER,
    complain                  INTEGER,
    response                  INTEGER,
    ingested_at               TIMESTAMP     DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────
-- INDEXES — Make queries fast
-- ─────────────────────────────────────────────────────

-- daily_metrics indexes (most queried table)
CREATE INDEX IF NOT EXISTS idx_daily_date
    ON daily_metrics(date DESC);

CREATE INDEX IF NOT EXISTS idx_daily_campaign_date
    ON daily_metrics(campaign_id, date DESC);

-- customers indexes
CREATE INDEX IF NOT EXISTS idx_customers_campaign
    ON customers(campaign_id, acquisition_date DESC);

CREATE INDEX IF NOT EXISTS idx_customers_channel
    ON customers(channel, acquisition_date DESC);

-- campaigns indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_channel
    ON campaigns(channel);

CREATE INDEX IF NOT EXISTS idx_campaigns_status
    ON campaigns(status);

-- ─────────────────────────────────────────────────────
-- KPI VIEWS
-- Pre-built queries for dashboard
-- ─────────────────────────────────────────────────────

-- View 1: Campaign Performance KPIs
CREATE OR REPLACE VIEW vw_campaign_kpis AS
SELECT
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.campaign_type,
    c.product,
    c.status,
    c.budget_total,

    -- Raw totals
    COALESCE(SUM(dm.spend),       0) AS total_spend,
    COALESCE(SUM(dm.revenue),     0) AS total_revenue,
    COALESCE(SUM(dm.impressions), 0) AS total_impressions,
    COALESCE(SUM(dm.clicks),      0) AS total_clicks,
    COALESCE(SUM(dm.leads),       0) AS total_leads,
    COALESCE(SUM(dm.conversions), 0) AS total_conversions,

    -- KPI calculations
    ROUND(
        (SUM(dm.revenue) - SUM(dm.spend))
        / NULLIF(SUM(dm.spend), 0) * 100,
    2) AS roi_pct,

    ROUND(
        SUM(dm.revenue)
        / NULLIF(SUM(dm.spend), 0),
    2) AS roas,

    ROUND(
        SUM(dm.spend)
        / NULLIF(SUM(dm.leads), 0),
    2) AS cpl,

    ROUND(
        SUM(dm.spend)
        / NULLIF(SUM(dm.conversions), 0),
    2) AS cpa,

    ROUND(
        SUM(dm.conversions)::NUMERIC
        / NULLIF(SUM(dm.clicks), 0) * 100,
    4) AS conversion_rate_pct,

    ROUND(
        SUM(dm.revenue) - SUM(dm.spend),
    2) AS gross_profit,

    -- Performance tier
    CASE
        WHEN (SUM(dm.revenue)-SUM(dm.spend))
             /NULLIF(SUM(dm.spend),0)*100 >= 200 THEN 'Excellent'
        WHEN (SUM(dm.revenue)-SUM(dm.spend))
             /NULLIF(SUM(dm.spend),0)*100 >= 100 THEN 'Good'
        WHEN (SUM(dm.revenue)-SUM(dm.spend))
             /NULLIF(SUM(dm.spend),0)*100 >= 0   THEN 'Break-even'
        ELSE 'Loss-making'
    END AS performance_tier

FROM campaigns c
LEFT JOIN daily_metrics dm ON c.campaign_id = dm.campaign_id
GROUP BY
    c.campaign_id, c.campaign_name, c.channel,
    c.campaign_type, c.product, c.status, c.budget_total;


-- View 2: Channel Comparison
CREATE OR REPLACE VIEW vw_channel_kpis AS
SELECT
    c.channel,
    COUNT(DISTINCT c.campaign_id)   AS total_campaigns,
    ROUND(SUM(dm.spend), 2)         AS total_spend,
    ROUND(SUM(dm.revenue), 2)       AS total_revenue,
    COALESCE(SUM(dm.leads), 0)      AS total_leads,
    COALESCE(SUM(dm.conversions),0) AS total_conversions,

    ROUND(
        (SUM(dm.revenue)-SUM(dm.spend))
        /NULLIF(SUM(dm.spend),0)*100,
    2) AS roi_pct,

    ROUND(
        SUM(dm.revenue)/NULLIF(SUM(dm.spend),0),
    2) AS roas,

    ROUND(
        SUM(dm.spend)/NULLIF(SUM(dm.leads),0),
    2) AS avg_cpl,

    -- Spend share across all channels
    ROUND(
        SUM(dm.spend)
        / SUM(SUM(dm.spend)) OVER () * 100,
    2) AS spend_share_pct

FROM campaigns c
LEFT JOIN daily_metrics dm ON c.campaign_id = dm.campaign_id
GROUP BY c.channel
ORDER BY roi_pct DESC NULLS LAST;


-- View 3: Weekly Trend
CREATE OR REPLACE VIEW vw_weekly_trend AS
SELECT
    DATE_TRUNC('week', date::timestamp)::date AS week_start,
    ROUND(SUM(spend), 2)                      AS weekly_spend,
    ROUND(SUM(revenue), 2)                    AS weekly_revenue,
    ROUND(
        (SUM(revenue)-SUM(spend))
        /NULLIF(SUM(spend),0)*100,
    2)                                         AS roi_pct,
    COALESCE(SUM(conversions), 0)             AS weekly_conversions,
    COALESCE(SUM(leads), 0)                   AS weekly_leads
FROM daily_metrics
GROUP BY DATE_TRUNC('week', date::timestamp)
ORDER BY week_start;