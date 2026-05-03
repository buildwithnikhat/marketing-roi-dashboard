# ingestion/data_cleaner.py

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

print("=" * 60)
print("  PHASE 3: DATA CLEANING")
print("=" * 60)


class CleaningReport:
    def __init__(self):
        self.changes = []

    def log(self, file: str, action: str, detail: str,
            rows_affected: int = 0):
        entry = {
            'file':          file,
            'action':        action,
            'detail':        detail,
            'rows_affected': int(rows_affected),
            'timestamp':     datetime.now().isoformat()
        }
        self.changes.append(entry)
        print(f"   📝 {action}: {detail} ({rows_affected} rows)")

    def save(self):
        os.makedirs("data/processed", exist_ok=True)
        clean_changes = []
        for change in self.changes:
            clean_change = {
                k: int(v) if hasattr(v, 'item') else v
                for k, v in change.items()
            }
            clean_changes.append(clean_change)
        with open("data/processed/cleaning_report.json", "w") as f:
            json.dump(clean_changes, f, indent=2)
        print(f"\n💾 Cleaning report saved: data/processed/cleaning_report.json")


report = CleaningReport()


# ═══════════════════════════════════════════════════════
# FILE 1: CLEAN KAGGLE DATA
# ═══════════════════════════════════════════════════════

def clean_kaggle_data() -> pd.DataFrame:
    print("\n" + "─" * 60)
    print("📂 CLEANING: marketing_campaign.csv")
    print("─" * 60)

    df = pd.read_csv("data/raw/marketing_campaign.csv",
                     dtype=str, sep=None, engine='python')
    print(f"   Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    original_rows = len(df)

    # CLEAN 1: Fix column names
    df.columns = df.columns.str.strip()
    report.log("kaggle", "Fix column names",
               "Stripped whitespace from all column names")

    # CLEAN 2: Drop useless columns
    useless_cols = ['Z_CostContact', 'Z_Revenue']
    existing_useless = [c for c in useless_cols if c in df.columns]
    if existing_useless:
        df = df.drop(columns=existing_useless)
        report.log("kaggle", "Drop useless columns",
                   f"Removed: {existing_useless}", len(df))

    # CLEAN 3: Fix data types
    numeric_cols = [
        'Income', 'Year_Birth', 'Kidhome', 'Teenhome',
        'Recency', 'MntWines', 'MntFruits', 'MntMeatProducts',
        'MntFishProducts', 'MntSweetProducts', 'MntGoldProds',
        'NumDealsPurchases', 'NumWebPurchases',
        'NumCatalogPurchases', 'NumStorePurchases',
        'NumWebVisitsMonth', 'AcceptedCmp1', 'AcceptedCmp2',
        'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5',
        'Complain', 'Response'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    report.log("kaggle", "Fix data types",
               f"Converted {len(numeric_cols)} columns to numeric")

    # CLEAN 4: Fix date column
    if 'Dt_Customer' in df.columns:
        df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'],
                                            errors='coerce')
        report.log("kaggle", "Fix date type",
                   "Dt_Customer converted to datetime")

    # CLEAN 5: Fill missing Income
    if 'Income' in df.columns:
        null_count = df['Income'].isna().sum()
        if null_count > 0:
            median_income = df['Income'].median()
            df['Income'] = df['Income'].fillna(median_income)
            report.log("kaggle", "Fill missing Income",
                       f"Filled {null_count} nulls with "
                       f"median: ₹{median_income:,.0f}",
                       int(null_count))

    # CLEAN 6: Create Age column
    if 'Year_Birth' in df.columns:
        df['Age'] = 2024 - df['Year_Birth']
        impossible = (df['Age'] < 18) | (df['Age'] > 90)
        impossible_count = impossible.sum()
        if impossible_count > 0:
            df = df[~impossible]
            report.log("kaggle", "Remove impossible ages",
                       f"Removed {impossible_count} rows",
                       int(impossible_count))
        report.log("kaggle", "Create Age column",
                   "Age = 2024 - Year_Birth", len(df))

    # CLEAN 7: Create Age Groups
    if 'Age' in df.columns:
        df['Age_Group'] = pd.cut(
            df['Age'],
            bins=[17, 25, 35, 45, 55, 90],
            labels=['18-24', '25-34', '35-44', '45-54', '55+']
        )
        report.log("kaggle", "Create Age_Group",
                   "Binned Age into 5 groups")

    # CLEAN 8: Total Spending
    spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts',
                  'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']
    existing_spend = [c for c in spend_cols if c in df.columns]
    if existing_spend:
        df['Total_Spending'] = df[existing_spend].sum(axis=1)
        report.log("kaggle", "Create Total_Spending",
                   f"Sum of {len(existing_spend)} columns", len(df))

    # CLEAN 9: Total Campaigns Accepted
    cmp_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3',
                'AcceptedCmp4', 'AcceptedCmp5']
    existing_cmp = [c for c in cmp_cols if c in df.columns]
    if existing_cmp:
        df['Total_Campaigns_Accepted'] = df[existing_cmp].sum(axis=1)
        report.log("kaggle", "Create Total_Campaigns_Accepted",
                   f"Sum of {len(existing_cmp)} columns", len(df))

    # CLEAN 10: Customer Tenure
    if 'Dt_Customer' in df.columns:
        ref = pd.Timestamp('2024-01-01')
        df['Tenure_Days']  = (ref - df['Dt_Customer']).dt.days
        df['Tenure_Years'] = (df['Tenure_Days'] / 365).round(1)
        report.log("kaggle", "Create Tenure columns",
                   "Days and years since joining", len(df))

    # CLEAN 11: Remove Income outliers
    if 'Income' in df.columns:
        Q1    = df['Income'].quantile(0.25)
        Q3    = df['Income'].quantile(0.75)
        IQR   = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((df['Income'] < lower) |
                    (df['Income'] > upper)).sum()
        df = df[(df['Income'] >= lower) & (df['Income'] <= upper)]
        report.log("kaggle", "Remove Income outliers",
                   f"Kept ₹{lower:,.0f} to ₹{upper:,.0f}. "
                   f"Removed {outliers}",
                   int(outliers))

    # CLEAN 12: Standardize Marital Status
    if 'Marital_Status' in df.columns:
        marital_map = {
            'Alone': 'Single', 'Absurd': 'Single',
            'Yolo':  'Single', 'Together': 'Partner',
            'Married': 'Partner', 'Divorced': 'Single',
            'Widow':  'Single',  'Single': 'Single',
        }
        df['Marital_Status'] = (df['Marital_Status']
                                 .str.strip()
                                 .map(marital_map)
                                 .fillna('Single'))
        report.log("kaggle", "Standardize Marital_Status",
                   "Mapped to: Single / Partner", len(df))

    # Summary
    print(f"\n   📊 CLEANING SUMMARY:")
    print(f"   Original rows: {original_rows}")
    print(f"   Clean rows:    {len(df)}")
    print(f"   Rows removed:  {original_rows - len(df)}")
    print(f"   Final columns: {df.shape[1]}")
    print(f"\n   New columns created:")
    for col in ['Age', 'Age_Group', 'Total_Spending',
                'Total_Campaigns_Accepted',
                'Tenure_Days', 'Tenure_Years']:
        if col in df.columns:
            print(f"   ✅ {col}")

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/kaggle_clean.csv", index=False)
    print(f"\n💾 Saved: data/processed/kaggle_clean.csv")
    return df


# ═══════════════════════════════════════════════════════
# FILE 2: CLEAN DAILY METRICS
# ═══════════════════════════════════════════════════════

def clean_daily_metrics() -> pd.DataFrame:
    print("\n" + "─" * 60)
    print("📂 CLEANING: daily_metrics.csv")
    print("─" * 60)

    df = pd.read_csv("data/raw/daily_metrics.csv", dtype=str)
    print(f"   Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    original_rows = len(df)

    # Fix data types
    numeric_cols = ['spend', 'impressions', 'clicks',
                    'leads', 'conversions', 'revenue',
                    'ctr', 'cpc']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col],
                                     errors='coerce').fillna(0)

    int_cols = ['impressions', 'clicks', 'leads', 'conversions']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    report.log("daily_metrics", "Fix data types",
               "Numeric and date columns fixed")

    # Business rule: clicks <= impressions
    violation = (df['clicks'] > df['impressions']).sum()
    if violation > 0:
        df.loc[df['clicks'] > df['impressions'],
               'clicks'] = df['impressions']
        report.log("daily_metrics", "Fix clicks > impressions",
                   f"Capped {violation} rows", int(violation))

    # Business rule: conversions <= clicks
    violation2 = (df['conversions'] > df['clicks']).sum()
    if violation2 > 0:
        df.loc[df['conversions'] > df['clicks'],
               'conversions'] = df['clicks']
        report.log("daily_metrics", "Fix conversions > clicks",
                   f"Capped {violation2} rows", int(violation2))

    # No negative values
    for col in ['spend', 'revenue', 'impressions',
                'clicks', 'leads', 'conversions']:
        if col in df.columns:
            neg = (df[col] < 0).sum()
            if neg > 0:
                df[col] = df[col].clip(lower=0)
                report.log("daily_metrics",
                           f"Fix negative {col}",
                           f"Clipped {neg} values", int(neg))

    # Recalculate CTR and CPC from clean data
    df['ctr'] = np.where(
        df['impressions'] > 0,
        (df['clicks'] / df['impressions'] * 100).round(4),
        0.0
    )
    df['cpc'] = np.where(
        df['clicks'] > 0,
        (df['spend'] / df['clicks']).round(2),
        0.0
    )
    report.log("daily_metrics", "Recalculate CTR and CPC",
               "Derived from clean data")

    # Remove duplicates
    dupes = df.duplicated(subset=['campaign_id', 'date']).sum()
    if dupes > 0:
        df = df.drop_duplicates(
            subset=['campaign_id', 'date'], keep='last'
        )
        report.log("daily_metrics", "Remove duplicates",
                   f"Removed {dupes} rows", int(dupes))

    # Remove null dates
    null_dates = df['date'].isna().sum()
    if null_dates > 0:
        df = df.dropna(subset=['date'])
        report.log("daily_metrics", "Remove null dates",
                   f"Removed {null_dates} rows", int(null_dates))

    print(f"\n   📊 CLEANING SUMMARY:")
    print(f"   Original rows: {original_rows}")
    print(f"   Clean rows:    {len(df)}")
    print(f"   Spend range:   ₹{df['spend'].min():,.0f}"
          f" - ₹{df['spend'].max():,.0f}")
    print(f"   Revenue range: ₹{df['revenue'].min():,.0f}"
          f" - ₹{df['revenue'].max():,.0f}")
    print(f"   CTR range:     {df['ctr'].min():.2f}%"
          f" - {df['ctr'].max():.2f}%")

    df.to_csv("data/processed/daily_metrics_clean.csv", index=False)
    print(f"\n💾 Saved: data/processed/daily_metrics_clean.csv")
    return df


# ═══════════════════════════════════════════════════════
# FILE 3: CLEAN CAMPAIGNS
# ═══════════════════════════════════════════════════════

def clean_campaigns() -> pd.DataFrame:
    print("\n" + "─" * 60)
    print("📂 CLEANING: campaigns.csv")
    print("─" * 60)

    df = pd.read_csv("data/raw/campaigns.csv", dtype=str)
    print(f"   Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    # Fix types
    df['budget_total'] = pd.to_numeric(df['budget_total'],
                                        errors='coerce')
    df['start_date']   = pd.to_datetime(df['start_date'],
                                         errors='coerce')
    df['end_date']     = pd.to_datetime(df['end_date'],
                                         errors='coerce')

    # Standardize text
    df['channel']       = df['channel'].str.strip()
    df['campaign_type'] = df['campaign_type'].str.strip()
    df['status']        = (df['status'].str.strip()
                             .str.capitalize())
    df['product']       = df['product'].str.strip()

    # Validate dates
    invalid_dates = (df['end_date'] < df['start_date']).sum()
    if invalid_dates > 0:
        df = df[df['end_date'] >= df['start_date']]
        report.log("campaigns", "Remove invalid date ranges",
                   f"{invalid_dates} rows removed",
                   int(invalid_dates))

    # Campaign duration
    df['duration_days'] = (df['end_date'] - df['start_date']).dt.days

    # Validate budget
    invalid_budget = (df['budget_total'] <= 0).sum()
    if invalid_budget > 0:
        df = df[df['budget_total'] > 0]
        report.log("campaigns", "Remove invalid budgets",
                   f"{invalid_budget} rows removed",
                   int(invalid_budget))

    report.log("campaigns", "Clean complete",
               f"{len(df)} valid campaigns", len(df))

    print(f"\n   📊 CLEANING SUMMARY:")
    print(f"   Valid campaigns: {len(df)}")
    print(f"   Channels: {df['channel'].unique().tolist()}")
    print(f"   Status:   {df['status'].value_counts().to_dict()}")
    print(f"   Avg duration: {df['duration_days'].mean():.0f} days")

    df.to_csv("data/processed/campaigns_clean.csv", index=False)
    print(f"\n💾 Saved: data/processed/campaigns_clean.csv")
    return df


# ═══════════════════════════════════════════════════════
# FILE 4: CLEAN CUSTOMERS
# ═══════════════════════════════════════════════════════

def clean_customers() -> pd.DataFrame:
    print("\n" + "─" * 60)
    print("📂 CLEANING: customers.csv")
    print("─" * 60)

    df = pd.read_csv("data/raw/customers.csv", dtype=str)
    print(f"   Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    original_rows = len(df)

    # Fix types
    df['first_purchase_value'] = pd.to_numeric(
        df['first_purchase_value'], errors='coerce').fillna(0)
    df['total_lifetime_value'] = pd.to_numeric(
        df['total_lifetime_value'], errors='coerce').fillna(0)
    df['total_orders']         = pd.to_numeric(
        df['total_orders'], errors='coerce').fillna(1).astype(int)
    df['acquisition_date']     = pd.to_datetime(
        df['acquisition_date'], errors='coerce')

    # Fix boolean
    bool_map = {
        'True': True,  'False': False,
        'true': True,  'false': False,
        '1':    True,  '0':     False
    }
    df['is_repeat_customer'] = (df['is_repeat_customer']
                                  .map(bool_map)
                                  .fillna(False))

    # Standardize city
    df['city'] = df['city'].str.strip().str.title()

    # Remove invalid purchases
    invalid = (df['first_purchase_value'] <= 0).sum()
    if invalid > 0:
        df = df[df['first_purchase_value'] > 0]
        report.log("customers", "Remove invalid purchases",
                   f"{invalid} rows removed", int(invalid))

    # Remove duplicate customers
    dupes = df.duplicated(subset=['customer_id']).sum()
    if dupes > 0:
        df = df.drop_duplicates(
            subset=['customer_id'], keep='last'
        )
        report.log("customers", "Remove duplicates",
                   f"Removed {dupes} rows", int(dupes))

    report.log("customers", "Clean complete",
               f"{len(df)} valid customers", len(df))

    print(f"\n   📊 CLEANING SUMMARY:")
    print(f"   Original rows:    {original_rows}")
    print(f"   Clean rows:       {len(df)}")
    print(f"   Cities:           {df['city'].nunique()} unique")
    print(f"   Repeat customers: {df['is_repeat_customer'].sum()}"
          f" ({df['is_repeat_customer'].mean()*100:.1f}%)")
    print(f"   Avg purchase:     "
          f"₹{df['first_purchase_value'].mean():,.0f}")

    df.to_csv("data/processed/customers_clean.csv", index=False)
    print(f"\n💾 Saved: data/processed/customers_clean.csv")
    return df


# ═══════════════════════════════════════════════════════
# MAIN RUN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    kaggle_df    = clean_kaggle_data()
    metrics_df   = clean_daily_metrics()
    campaigns_df = clean_campaigns()
    customers_df = clean_customers()

    report.save()

    print("\n" + "=" * 60)
    print("  ✅ ALL FILES CLEANED SUCCESSFULLY")
    print("=" * 60)
    print(f"  kaggle_clean.csv        → {len(kaggle_df):,} rows")
    print(f"  daily_metrics_clean.csv → {len(metrics_df):,} rows")
    print(f"  campaigns_clean.csv     → {len(campaigns_df):,} rows")
    print(f"  customers_clean.csv     → {len(customers_df):,} rows")
    print(f"\n  All saved in: data/processed/")
    print("=" * 60)