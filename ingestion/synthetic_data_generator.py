# ingestion/synthetic_data_generator.py

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import json

fake = Faker('en_IN')
np.random.seed(99)
random.seed(99)

print("=" * 60)
print("  SYNTHETIC DATA GENERATION")
print("=" * 60)

CHANNELS = ['Google Search', 'Google Display', 'Meta Feed',
            'Meta Stories', 'Email', 'SMS', 'YouTube']

CAMPAIGN_TYPES = ['Brand Awareness', 'Lead Generation',
                  'Retargeting', 'Conversion', 'Traffic']

PRODUCTS = ['Skincare Basic Kit', 'Premium Serum',
            'Anti-Aging Bundle', 'Moisturizer', 'SPF Bundle']

CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad',
          'Chennai', 'Pune', 'Ahmedabad', 'Kolkata']

CHANNEL_PROFILES = {
    'Google Search':  {'ctr': (0.03, 0.08),  'conv': (0.001, 0.005), 'cpm': (80, 180),  'aov': (500, 2000),  'lead': (0.05, 0.15)},
    'Google Display': {'ctr': (0.005, 0.02), 'conv': (0.0005,0.002), 'cpm': (30, 80),   'aov': (400, 1500),  'lead': (0.02, 0.08)},
    'Meta Feed':      {'ctr': (0.01, 0.05),  'conv': (0.001, 0.004), 'cpm': (60, 150),  'aov': (450, 1800),  'lead': (0.04, 0.12)},
    'Meta Stories':   {'ctr': (0.008, 0.03), 'conv': (0.001, 0.003), 'cpm': (50, 130),  'aov': (400, 1600),  'lead': (0.03, 0.10)},
    'Email':          {'ctr': (0.15, 0.35),  'conv': (0.005, 0.015), 'cpm': (5, 20),    'aov': (500, 2000),  'lead': (0.10, 0.25)},
    'SMS':            {'ctr': (0.10, 0.25),  'conv': (0.003, 0.010), 'cpm': (8, 25),    'aov': (450, 1800),  'lead': (0.08, 0.20)},
    'YouTube':        {'ctr': (0.003, 0.01), 'conv': (0.0005,0.002), 'cpm': (100, 250), 'aov': (600, 2500),  'lead': (0.02, 0.08)},
}


def generate_campaigns(n=20):
    print(f"\n📦 Generating {n} campaigns...")
    rows = []
    for i in range(n):
        channel   = random.choice(CHANNELS)
        start     = fake.date_between(datetime(2024,1,1), datetime(2024,10,1))
        end       = start + timedelta(days=random.randint(14, 90))
        rows.append({
            'campaign_id':     f'CAMP_{1000+i}',
            'campaign_name':   f'{random.choice(PRODUCTS)} - {random.choice(CAMPAIGN_TYPES)} - {channel}',
            'channel':         channel,
            'campaign_type':   random.choice(CAMPAIGN_TYPES),
            'product':         random.choice(PRODUCTS),
            'target_audience': random.choice(['18-24','25-34','35-44','45-54','55+']),
            'budget_total':    round(random.uniform(10000, 500000), 2),
            'start_date':      start,
            'end_date':        end,
            'status':          random.choice(['Active','Active','Active','Paused','Completed']),
        })
    df = pd.DataFrame(rows)
    print(f"   ✅ {len(df)} campaigns created")
    return df


def generate_daily_metrics(campaigns_df):
    print(f"\n📊 Generating daily metrics...")
    records = []
    for _, c in campaigns_df.iterrows():
        p      = CHANNEL_PROFILES[c['channel']]
        dates  = pd.date_range(c['start_date'], c['end_date'], freq='D')
        budget = float(c['budget_total'])

        for date in dates:
            # Weekday effect
            mult   = 1.3 if date.weekday() < 4 else 0.7
            spend  = round(budget / len(dates) * mult * random.uniform(0.7, 1.3), 2)
            impr   = int((spend / random.uniform(*p['cpm'])) * 1000)
            clicks = min(int(impr * random.uniform(*p['ctr'])), impr)
            leads  = int(clicks * random.uniform(*p['lead']))
            convs  = min(int(clicks * random.uniform(*p['conv'])), 5)
            rev    = round(convs * random.uniform(*p['aov']) * random.uniform(2.5, 4.0), 2)

            records.append({
                'record_id':   f'REC_{len(records):07d}',
                'campaign_id': c['campaign_id'],
                'date':        date.date(),
                'spend':       spend,
                'impressions': impr,
                'clicks':      clicks,
                'leads':       leads,
                'conversions': convs,
                'revenue':     rev,
                'ctr':         round(clicks/impr*100, 4) if impr > 0 else 0,
                'cpc':         round(spend/clicks, 2)    if clicks > 0 else 0,
                'data_source': 'synthetic',
            })

    df = pd.DataFrame(records)
    print(f"   ✅ {len(df):,} daily records created")
    print(f"   📅 Range: {df['date'].min()} → {df['date'].max()}")
    print(f"   💰 Total spend:   ₹{df['spend'].sum():,.0f}")
    print(f"   💵 Total revenue: ₹{df['revenue'].sum():,.0f}")
    roi = (df['revenue'].sum()-df['spend'].sum())/df['spend'].sum()*100
    print(f"   📈 Overall ROI:   {roi:.1f}%")
    return df


def generate_customers(daily_df, campaigns_df):
    print(f"\n👥 Generating customers...")
    rows = []
    num  = 1
    for _, row in daily_df.iterrows():
        if row['conversions'] <= 0:
            continue
        camp = campaigns_df[campaigns_df['campaign_id']==row['campaign_id']].iloc[0]
        for _ in range(min(int(row['conversions']), 3)):
            val = round(random.uniform(500, 8000), 2)
            rows.append({
                'customer_id':          f'CUST_{num:06d}',
                'campaign_id':          row['campaign_id'],
                'channel':              camp['channel'],
                'acquisition_date':     row['date'],
                'first_purchase_value': val,
                'email':                fake.email(),
                'city':                 random.choice(CITIES),
                'age_group':            camp['target_audience'],
                'is_repeat_customer':   random.choice([False,False,False,True]),
                'total_lifetime_value': val,
                'total_orders':         1,
            })
            num += 1
    df = pd.DataFrame(rows)
    print(f"   ✅ {len(df):,} customers created")
    return df


def save_all(campaigns, daily, customers):
    os.makedirs("data/raw", exist_ok=True)
    campaigns.to_csv("data/raw/campaigns.csv",      index=False)
    daily.to_csv("data/raw/daily_metrics.csv",      index=False)
    customers.to_csv("data/raw/customers.csv",      index=False)

    meta = {
        'generated_at':  datetime.now().isoformat(),
        'campaigns':     len(campaigns),
        'daily_records': len(daily),
        'customers':     len(customers),
        'total_spend':   float(daily['spend'].sum()),
        'total_revenue': float(daily['revenue'].sum()),
    }
    with open("data/raw/metadata.json","w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n💾 FILES SAVED:")
    for fname in ['campaigns.csv','daily_metrics.csv','customers.csv','metadata.json']:
        size = os.path.getsize(f"data/raw/{fname}") / 1024
        print(f"   data/raw/{fname:<25} {size:.1f} KB")


# ── RUN ───────────────────────────────────────────────
if __name__ == "__main__":
    c = generate_campaigns(20)
    d = generate_daily_metrics(c)
    cu = generate_customers(d, c)
    save_all(c, d, cu)

    print("\n" + "="*60)
    print("  ✅ ALL DATA GENERATED SUCCESSFULLY")
    print(f"  Campaigns:  {len(c)}")
    print(f"  Daily rows: {len(d):,}")
    print(f"  Customers:  {len(cu):,}")
    print("="*60)