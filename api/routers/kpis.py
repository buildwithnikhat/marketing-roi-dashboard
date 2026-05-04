# api/routers/kpis.py

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import time

from api.database import run_query, df_to_records, safe_float
from api.models import APIResponse

router = APIRouter(prefix="/kpis", tags=["KPIs"])


# ═══════════════════════════════════════════════════════
# ENDPOINT 1: Portfolio Summary
# GET /api/v1/kpis/summary
# Powers the dashboard header KPI cards
# ═══════════════════════════════════════════════════════

@router.get("/summary")
async def get_summary():
    """
    Returns single-value KPIs for dashboard header.
    ROI, ROAS, CPL, total spend, revenue, conversions.
    """
    start = time.time()
    try:
        sql = """
            SELECT
                ROUND(SUM(spend), 2)        AS total_spend,
                ROUND(SUM(revenue), 2)      AS total_revenue,
                ROUND(SUM(revenue)
                      - SUM(spend), 2)      AS gross_profit,
                ROUND(
                    (SUM(revenue)-SUM(spend))
                    /NULLIF(SUM(spend),0)*100,
                2)                          AS roi_pct,
                ROUND(
                    SUM(revenue)
                    /NULLIF(SUM(spend),0),
                2)                          AS roas,
                ROUND(
                    SUM(spend)
                    /NULLIF(SUM(leads),0),
                2)                          AS cpl,
                ROUND(
                    SUM(conversions)::NUMERIC
                    /NULLIF(SUM(clicks),0)*100,
                2)                          AS conversion_rate_pct,
                SUM(impressions)            AS total_impressions,
                SUM(clicks)                 AS total_clicks,
                SUM(leads)                  AS total_leads,
                SUM(conversions)            AS total_conversions
            FROM daily_metrics
        """
        df  = run_query(sql)
        row = df.iloc[0]

        data = {
            'total_spend':          safe_float(row['total_spend']),
            'total_revenue':        safe_float(row['total_revenue']),
            'gross_profit':         safe_float(row['gross_profit']),
            'roi_pct':              safe_float(row['roi_pct']),
            'roas':                 safe_float(row['roas']),
            'cpl':                  safe_float(row['cpl']),
            'conversion_rate_pct':  safe_float(
                                        row['conversion_rate_pct']),
            'total_impressions':    int(row['total_impressions'] or 0),
            'total_clicks':         int(row['total_clicks'] or 0),
            'total_leads':          int(row['total_leads'] or 0),
            'total_conversions':    int(row['total_conversions'] or 0),
        }

        return APIResponse.ok(
            data,
            query_ms=round((time.time()-start)*1000, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# ENDPOINT 2: Channel KPIs
# GET /api/v1/kpis/channels
# Powers the channel comparison charts
# ═══════════════════════════════════════════════════════

@router.get("/channels")
async def get_channel_kpis():
    """
    Returns KPIs grouped by channel.
    ROI, ROAS, CPL, spend share per channel.
    """
    start = time.time()
    try:
        sql = """
            SELECT
                c.channel,
                COUNT(DISTINCT c.campaign_id) AS total_campaigns,
                ROUND(SUM(dm.spend), 2)        AS total_spend,
                ROUND(SUM(dm.revenue), 2)      AS total_revenue,
                ROUND(
                    SUM(dm.revenue)-SUM(dm.spend),
                2)                             AS profit,
                ROUND(
                    (SUM(dm.revenue)-SUM(dm.spend))
                    /NULLIF(SUM(dm.spend),0)*100,
                2)                             AS roi_pct,
                ROUND(
                    SUM(dm.revenue)
                    /NULLIF(SUM(dm.spend),0),
                2)                             AS roas,
                ROUND(
                    SUM(dm.spend)
                    /NULLIF(SUM(dm.leads),0),
                2)                             AS cpl,
                COALESCE(SUM(dm.leads),0)      AS total_leads,
                COALESCE(SUM(dm.conversions),0)AS total_conversions,
                ROUND(
                    SUM(dm.spend)
                    /SUM(SUM(dm.spend)) OVER()*100,
                2)                             AS spend_share_pct
            FROM campaigns c
            JOIN daily_metrics dm
                ON c.campaign_id = dm.campaign_id
            GROUP BY c.channel
            ORDER BY roi_pct DESC NULLS LAST
        """
        df      = run_query(sql)
        records = df_to_records(df)

        return APIResponse.ok(
            records,
            count=len(records),
            query_ms=round((time.time()-start)*1000, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# ENDPOINT 3: Campaign KPIs
# GET /api/v1/kpis/campaigns
# Powers the campaign table with filters
# ═══════════════════════════════════════════════════════

@router.get("/campaigns")
async def get_campaign_kpis(
    channel: Optional[str] = Query(
        None, description="Filter by channel"),
    status:  Optional[str] = Query(
        None, description="Filter by status"),
    min_roi: Optional[float] = Query(
        None, description="Minimum ROI %"),
):
    """
    Returns KPIs per campaign with optional filters.

    Examples:
      /kpis/campaigns?channel=Email
      /kpis/campaigns?status=Active&min_roi=100
    """
    start = time.time()
    try:
        sql = """
            SELECT
                campaign_id,
                campaign_name,
                channel,
                campaign_type,
                product,
                status,
                budget_total,
                total_spend,
                total_revenue,
                gross_profit,
                roi_pct,
                roas,
                cpl,
                conversion_rate_pct,
                total_leads,
                total_conversions,
                performance_tier
            FROM vw_campaign_kpis
            WHERE
                (:channel IS NULL OR channel = :channel)
                AND (:status  IS NULL OR status  = :status)
                AND (:min_roi IS NULL OR roi_pct >= :min_roi)
            ORDER BY roi_pct DESC NULLS LAST
        """
        df = run_query(sql, {
            'channel': channel,
            'status':  status,
            'min_roi': min_roi,
        })
        records = df_to_records(df)

        return APIResponse.ok(
            records,
            count=len(records),
            filters={
                'channel': channel,
                'status':  status,
                'min_roi': min_roi
            },
            query_ms=round((time.time()-start)*1000, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# ENDPOINT 4: Weekly Trend
# GET /api/v1/kpis/trends
# Powers the ROI trend line chart
# ═══════════════════════════════════════════════════════

@router.get("/trends")
async def get_weekly_trend(
    weeks: int = Query(
        12, ge=4, le=52,
        description="Number of weeks to return")
):
    """
    Returns weekly ROI trend data.
    Default: last 12 weeks.
    """
    start = time.time()
    try:
        sql = """
            SELECT * FROM (
                SELECT
                    DATE_TRUNC('week',
                        date::timestamp)::date  AS week_start,
                    ROUND(SUM(spend),2)         AS weekly_spend,
                    ROUND(SUM(revenue),2)       AS weekly_revenue,
                    ROUND(
                        (SUM(revenue)-SUM(spend))
                        /NULLIF(SUM(spend),0)*100,
                    2)                          AS roi_pct,
                    COALESCE(SUM(leads),0)      AS weekly_leads,
                    COALESCE(SUM(conversions),0)AS weekly_conversions,
                    LAG(ROUND(
                        (SUM(revenue)-SUM(spend))
                        /NULLIF(SUM(spend),0)*100,
                    2)) OVER (
                        ORDER BY DATE_TRUNC('week',date::timestamp)
                    )                           AS prev_week_roi
                FROM daily_metrics
                GROUP BY DATE_TRUNC('week', date::timestamp)
                ORDER BY week_start DESC
                LIMIT :weeks
            ) t
            ORDER BY week_start ASC
        """
        df      = run_query(sql, {'weeks': weeks})
        records = df_to_records(df)

        return APIResponse.ok(
            records,
            count=len(records),
            weeks=weeks,
            query_ms=round((time.time()-start)*1000, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════
# ENDPOINT 5: Anomalies
# GET /api/v1/kpis/anomalies
# Powers the anomaly detection panel
# ═══════════════════════════════════════════════════════

@router.get("/anomalies")
async def get_anomalies(
    z_threshold: float = Query(
        2.0, ge=1.0, le=4.0,
        description="Z-score threshold")
):
    """
    Returns statistically anomalous campaign days.
    Z-score > 2.0 = unusual performance (good or bad).
    """
    start = time.time()
    try:
        sql = """
            WITH stats AS (
                SELECT
                    campaign_id,
                    AVG((revenue-spend)
                        /NULLIF(spend,0)*100)    AS avg_roi,
                    STDDEV((revenue-spend)
                        /NULLIF(spend,0)*100)    AS std_roi
                FROM daily_metrics
                WHERE spend > 0
                GROUP BY campaign_id
                HAVING COUNT(*) >= 7
            )
            SELECT
                dm.date,
                dm.campaign_id,
                c.channel,
                c.campaign_name,
                ROUND(dm.spend,2)    AS spend,
                ROUND(dm.revenue,2)  AS revenue,
                ROUND(
                    (dm.revenue-dm.spend)
                    /NULLIF(dm.spend,0)*100,
                2)                   AS daily_roi_pct,
                ROUND(s.avg_roi,2)   AS avg_roi,
                ROUND(
                    ((dm.revenue-dm.spend)
                     /NULLIF(dm.spend,0)*100 - s.avg_roi)
                    /NULLIF(s.std_roi,0),
                2)                   AS z_score
            FROM daily_metrics dm
            JOIN campaigns c
                ON dm.campaign_id = c.campaign_id
            JOIN stats s
                ON dm.campaign_id = s.campaign_id
            WHERE ABS(
                ((dm.revenue-dm.spend)
                 /NULLIF(dm.spend,0)*100 - s.avg_roi)
                /NULLIF(s.std_roi,0)
            ) > :threshold
            ORDER BY ABS(z_score) DESC
            LIMIT 20
        """
        df      = run_query(sql, {'threshold': z_threshold})
        records = df_to_records(df)

        return APIResponse.ok(
            records,
            count=len(records),
            z_threshold=z_threshold,
            query_ms=round((time.time()-start)*1000, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))