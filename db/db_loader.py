# db/db_loader.py
# Loads all cleaned CSV files into PostgreSQL

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

print("=" * 60)
print("  DATABASE LOADER")
print("=" * 60)

# ── Connect to database ───────────────────────────────
def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        dbname=os.getenv('DB_NAME', 'marketing_roi_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )

def clean_value(v):
    """Convert numpy/pandas types to Python native types."""
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if hasattr(v, 'item'):
        return v.item()
    return v

def load_table(conn, df, columns, sql, table_name):
    """Bulk load a DataFrame into PostgreSQL."""
    records = [
        tuple(clean_value(row[c]) for c in columns)
        for _, row in df.iterrows()
    ]
    cursor = conn.cursor()
    try:
        execute_values(cursor, sql, records, page_size=500)
        conn.commit()
        print(f"   ✅ {table_name}: {len(records):,} rows loaded")
    except Exception as e:
        conn.rollback()
        print(f"   ❌ {table_name} failed: {e}")
    finally:
        cursor.close()


# ═══════════════════════════════════════════════════════
# LOAD 1: CAMPAIGNS
# ═══════════════════════════════════════════════════════

def load_campaigns(conn):
    print("\n📦 Loading campaigns...")
    df = pd.read_csv("data/processed/campaigns_clean.csv")

    columns = [
        'campaign_id', 'campaign_name', 'channel',
        'campaign_type', 'product', 'target_audience',
        'budget_total', 'start_date', 'end_date',
        'status', 'duration_days'
    ]

    sql = """
        INSERT INTO campaigns (
            campaign_id, campaign_name, channel,
            campaign_type, product, target_audience,
            budget_total, start_date, end_date,
            status, duration_days
        ) VALUES %s
        ON CONFLICT (campaign_id) DO UPDATE SET
            status     = EXCLUDED.status,
            updated_at = NOW()
    """
    load_table(conn, df, columns, sql, "campaigns")


# ═══════════════════════════════════════════════════════
# LOAD 2: DAILY METRICS
# ═══════════════════════════════════════════════════════

def load_daily_metrics(conn):
    print("\n📊 Loading daily metrics...")
    df = pd.read_csv("data/processed/daily_metrics_clean.csv")

    columns = [
        'record_id', 'campaign_id', 'date', 'spend',
        'impressions', 'clicks', 'leads', 'conversions',
        'revenue', 'ctr', 'cpc', 'data_source'
    ]

    sql = """
        INSERT INTO daily_metrics (
            record_id, campaign_id, date, spend,
            impressions, clicks, leads, conversions,
            revenue, ctr, cpc, data_source
        ) VALUES %s
        ON CONFLICT (campaign_id, date) DO UPDATE SET
            spend       = EXCLUDED.spend,
            revenue     = EXCLUDED.revenue,
            impressions = EXCLUDED.impressions,
            clicks      = EXCLUDED.clicks,
            leads       = EXCLUDED.leads,
            conversions = EXCLUDED.conversions,
            ingested_at = NOW()
    """
    load_table(conn, df, columns, sql, "daily_metrics")


# ═══════════════════════════════════════════════════════
# LOAD 3: CUSTOMERS
# ═══════════════════════════════════════════════════════

def load_customers(conn):
    print("\n👥 Loading customers...")
    df = pd.read_csv("data/processed/customers_clean.csv")

    columns = [
        'customer_id', 'campaign_id', 'channel',
        'acquisition_date', 'first_purchase_value',
        'email', 'city', 'age_group',
        'is_repeat_customer', 'total_lifetime_value',
        'total_orders'
    ]

    sql = """
        INSERT INTO customers (
            customer_id, campaign_id, channel,
            acquisition_date, first_purchase_value,
            email, city, age_group,
            is_repeat_customer, total_lifetime_value,
            total_orders
        ) VALUES %s
        ON CONFLICT (customer_id) DO UPDATE SET
            total_lifetime_value = EXCLUDED.total_lifetime_value,
            total_orders         = EXCLUDED.total_orders
    """
    load_table(conn, df, columns, sql, "customers")


# ═══════════════════════════════════════════════════════
# LOAD 4: KAGGLE CUSTOMERS
# ═══════════════════════════════════════════════════════

def load_kaggle_customers(conn):
    print("\n📋 Loading Kaggle customer data...")
    df = pd.read_csv("data/processed/kaggle_clean.csv")

    # Rename columns to match our schema
    col_map = {
        'ID':                       'id',
        'Year_Birth':               'year_birth',
        'Age':                      'age',
        'Age_Group':                'age_group',
        'Education':                'education',
        'Marital_Status':           'marital_status',
        'Income':                   'income',
        'Kidhome':                  'kidhome',
        'Teenhome':                 'teenhome',
        'Dt_Customer':              'dt_customer',
        'Tenure_Days':              'tenure_days',
        'Tenure_Years':             'tenure_years',
        'Recency':                  'recency',
        'Total_Spending':           'total_spending',
        'MntWines':                 'mnt_wines',
        'MntFruits':                'mnt_fruits',
        'MntMeatProducts':          'mnt_meat_products',
        'MntFishProducts':          'mnt_fish_products',
        'MntSweetProducts':         'mnt_sweet_products',
        'MntGoldProds':             'mnt_gold_prods',
        'NumDealsPurchases':        'num_deals_purchases',
        'NumWebPurchases':          'num_web_purchases',
        'NumCatalogPurchases':      'num_catalog_purchases',
        'NumStorePurchases':        'num_store_purchases',
        'NumWebVisitsMonth':        'num_web_visits_month',
        'Total_Campaigns_Accepted': 'total_campaigns_accepted',
        'Complain':                 'complain',
        'Response':                 'response',
    }
    df = df.rename(columns=col_map)

    columns = [
        'id', 'year_birth', 'age', 'age_group',
        'education', 'marital_status', 'income',
        'kidhome', 'teenhome', 'dt_customer',
        'tenure_days', 'tenure_years', 'recency',
        'total_spending', 'mnt_wines', 'mnt_fruits',
        'mnt_meat_products', 'mnt_fish_products',
        'mnt_sweet_products', 'mnt_gold_prods',
        'num_deals_purchases', 'num_web_purchases',
        'num_catalog_purchases', 'num_store_purchases',
        'num_web_visits_month', 'total_campaigns_accepted',
        'complain', 'response'
    ]

    # Keep only columns that exist
    columns = [c for c in columns if c in df.columns]

    sql = f"""
        INSERT INTO kaggle_customers ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """
    load_table(conn, df, columns, sql, "kaggle_customers")


# ═══════════════════════════════════════════════════════
# VERIFY LOADED DATA
# ═══════════════════════════════════════════════════════

def verify_data(conn):
    print("\n🔍 VERIFYING LOADED DATA:")
    cursor = conn.cursor()

    tables = [
        'campaigns', 'daily_metrics',
        'customers', 'kaggle_customers'
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   ✅ {table:<25} {count:,} rows")

    # Test KPI view
    cursor.execute("SELECT COUNT(*) FROM vw_campaign_kpis")
    count = cursor.fetchone()[0]
    print(f"   ✅ {'vw_campaign_kpis':<25} {count:,} rows")

    # Quick KPI check
    print("\n📈 QUICK KPI CHECK:")
    cursor.execute("""
        SELECT
            ROUND(SUM(spend),2)   AS total_spend,
            ROUND(SUM(revenue),2) AS total_revenue,
            ROUND((SUM(revenue)-SUM(spend))
                  /NULLIF(SUM(spend),0)*100,2) AS roi_pct
        FROM daily_metrics
    """)
    row = cursor.fetchone()
    print(f"   Total Spend:   ₹{row[0]:,.0f}")
    print(f"   Total Revenue: ₹{row[1]:,.0f}")
    print(f"   Overall ROI:   {row[2]}%")

    cursor.close()


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    conn = get_connection()
    print("✅ Connected to PostgreSQL")

    # Load in order — campaigns first (parent table)
    load_campaigns(conn)
    load_daily_metrics(conn)
    load_customers(conn)
    load_kaggle_customers(conn)

    verify_data(conn)

    conn.close()

    print("\n" + "=" * 60)
    print("  ✅ ALL DATA LOADED INTO POSTGRESQL")
    print("=" * 60)

    