# ingestion/01_explore_kaggle_data.py

import pandas as pd
import os

print("=" * 60)
print("  RAW DATA EXPLORATION")
print("=" * 60)

# Load the CSV
filepath = "data/raw/marketing_campaign.csv"
print(f"\n📂 Loading: {filepath}")

# Read as string first — never assume data types
df = pd.read_csv(filepath, dtype=str, sep=None, engine='python')

# Shape
print(f"\n📐 SHAPE:")
print(f"   Rows:    {df.shape[0]:,}")
print(f"   Columns: {df.shape[1]}")

# Columns
print(f"\n📋 COLUMNS & SAMPLE VALUES:")
for col in df.columns:
    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else "EMPTY"
    nulls  = df[col].isna().sum()
    null_pct = nulls / len(df) * 100
    print(f"   {col:<30} sample: {str(sample):<20} nulls: {null_pct:.1f}%")

# First 3 rows
print(f"\n👀 FIRST 3 ROWS:")
print(df.head(3).to_string())

# Duplicates
dupes = df.duplicated().sum()
print(f"\n🔍 QUALITY:")
print(f"   Duplicate rows: {dupes}")
print(f"   Total nulls:    {df.isna().sum().sum()}")

print("\n✅ Exploration complete!")