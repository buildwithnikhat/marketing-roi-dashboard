````md
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=7F77DD&height=220&section=header&text=Marketing%20ROI%20Dashboard&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=AI-Powered%20Campaign%20Intelligence%20Platform%20by%20Nikhat%20Shaikh&descAlignY=55&descAlign=50&descSize=18" width="100%"/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.31-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Claude%20AI-Anthropic-7F77DD?style=for-the-badge&logo=anthropic&logoColor=white"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-1D9E75?style=flat-square"/>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-1D9E75?style=flat-square"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-7F77DD?style=flat-square"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️%20in%20India-EF9F27?style=flat-square"/>
  <img src="https://img.shields.io/github/stars/YOUR_GITHUB_USERNAME/marketing-roi-dashboard?style=flat-square&color=yellow"/>
  <img src="https://img.shields.io/github/forks/YOUR_GITHUB_USERNAME/marketing-roi-dashboard?style=flat-square&color=blue"/>
</p>

<p align="center">
  <a href="https://linkedin.com/in/YOUR_LINKEDIN_SLUG">
    <img src="https://img.shields.io/badge/LinkedIn-Nikhat%20Shaikh-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a>
  <a href="mailto:YOUR_EMAIL_HERE">
    <img src="https://img.shields.io/badge/Email-Hire%20Me-EA4335?style=for-the-badge&logo=gmail&logoColor=white"/>
  </a>
  <a href="https://YOUR_PORTFOLIO_URL">
    <img src="https://img.shields.io/badge/Portfolio-View%20My%20Work-7F77DD?style=for-the-badge&logo=vercel&logoColor=white"/>
  </a>
  <a href="https://github.com/YOUR_GITHUB_USERNAME">
    <img src="https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
</p>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&pause=1000&color=7F77DD&center=true&vCenter=true&width=700&lines=One+command.+Full+stack.+Real-time+AI+insights.;Ask+your+data+questions+in+plain+English.;From+raw+CSV+to+AI-powered+dashboard+%E2%80%94+end+to+end." alt="Typing SVG"/>

```bash
git clone https://github.com/buildwithnikhat/marketing-roi-dashboard.git
cd marketing-roi-dashboard
./scripts/init.sh
# 🚀 Dashboard live at http://localhost:8501
````

</div>

---

## 🎯 The Business Problem I Solved

> *Marketing teams I studied spend 3 days per week manually pulling data from Google Ads, Meta, and CRM into Excel. By the time the report is ready, the data is stale — and campaigns running at negative ROI go unnoticed for weeks.*

**Before this system:**

| Pain Point        | Reality                                               |
| ----------------- | ----------------------------------------------------- |
| 📊 Reporting time | 3 days of manual Excel work per week                  |
| 🔀 Data silos     | Google Ads, Meta, CRM — all completely separate       |
| 🤔 Decision speed | "Which channel is profitable?" takes 2 days to answer |
| 💸 Budget waste   | Campaigns at −20% ROI run for weeks undetected        |
| 🤖 AI insights    | Zero — just raw numbers on a spreadsheet              |

**After this system:**

| Outcome           | Result                                                       |
| ----------------- | ------------------------------------------------------------ |
| ⚡ Reporting time  | Real-time, always up to date                                 |
| 🔗 Unified data   | All channels in one PostgreSQL database                      |
| 🚀 Decision speed | Answer any question in under 3 seconds                       |
| 💰 ROI visibility | Every campaign tracked, loss-makers flagged instantly        |
| 🧠 AI analyst     | Ask "Why did ROI drop?" in plain English — get a real answer |

---

## 📸 Screenshots

<div align="center">

### 📊 Dashboard Overview — KPI Cards

<img src="screenshots/01_dashboard_overview.png" width="90%" />

<br/><br/>

### 📈 ROI Trend + Spend vs Revenue

<img src="screenshots/02_roi_trend_chart.png" width="90%" />

<br/><br/>

### 📡 Channel Performance Comparison

<img src="screenshots/03_channel_comparison.png" width="90%" />

<br/><br/>

### 🚨 Anomaly Detection Panel

<img src="screenshots/04_anomaly_detection.png" width="90%" />

</div>

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    END-TO-END ARCHITECTURE                         │
│                                                                     │
│  DATA SOURCES          ETL LAYER              STORAGE               │
│  ─────────────         ──────────             ───────               │
│  Google Ads API ──►                                                 │
│  Meta Ads API   ──►   Python ETL         ──►  PostgreSQL 16         │
│  CSV / Kaggle   ──►   • Validate                4 core tables       │
│  Synthetic Gen  ──►   • Transform               5 KPI views         │
│                       • Quarantine bad rows     Indexed for speed   │
│                                                                     │
│  KPI SQL LAYER         REST API LAYER         PRESENTATION          │
│  ──────────────        ──────────────         ────────────          │
│  SQL Views        ──►  FastAPI           ──►  Streamlit Dashboard   │
│  ROI, CPL, CAC         /api/v1/kpis            KPI Cards            │
│  ROAS, Anomalies       /api/v1/channels        Plotly Charts        │
│  Trend Analysis        /api/v1/ai/query        AI Chat Panel        │
│                        In-memory cache          CSV Export           │
│                                                                     │
│  AI INTELLIGENCE PIPELINE                                           │
│  ─────────────────────────                                          │
│  Question ──► SQL Generator ──► SQL Validator                       │
│  ──► PostgreSQL Executor ──► Insight Generator (temp=0.3)           │
│  ──► Business answer in plain English + supporting data             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 How the AI Pipeline Works

```text
User: "Which channel had the best ROI last month?"
         │
         ▼
┌─────────────────────────┐
│   SQL GENERATOR         │  temperature = 0
│   Schema context + NL   │  Deterministic — no creativity in SQL
│   → precise SQL query   │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   SQL VALIDATOR         │  Blocks: DROP · DELETE · INSERT
│   Safety + whitelist    │  UPDATE · pg_user · multi-statement
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   SQL EXECUTOR          │  15s timeout · 500 row hard limit
│   PostgreSQL query      │  Self-heals on syntax errors
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   INSIGHT GENERATOR     │  temperature = 0.3
│   Data → Business lang  │  Specific numbers + recommendation
└─────────────────────────┘
         │
         ▼

Answer: "Email delivered the highest ROI at 342.5%, outperforming
Google Search (287.3%) by 55 percentage points. Despite the lowest
spend at ₹2.85L, it generated ₹12.6L in revenue — a 4.4× ROAS.
Recommendation: Reallocate 15-20% of Meta Stories budget to Email."
```
