# check_setup.py
# Run this to verify your entire setup is correct

import sys
import importlib

print("=" * 55)
print("  MARKETING ROI DASHBOARD — SETUP VERIFICATION")
print("=" * 55)

# ── Python version check ──────────────────────────────
print(f"\n✅ Python version: {sys.version.split()[0]}")

# ── Package check ─────────────────────────────────────
packages = {
    "pandas":       "Data processing",
    "numpy":        "Numerical operations",
    "requests":     "HTTP / API calls",
    "faker":        "Synthetic data generation",
    "sqlalchemy":   "Database ORM",
    "psycopg2":     "PostgreSQL connector",
    "fastapi":      "REST API framework",
    "streamlit":    "Dashboard framework",
    "plotly":       "Interactive charts",
    "anthropic":    "Claude AI",
    "dotenv":       "Environment variables",
    "bs4":          "Web scraping",
    "openpyxl":     "Excel file support",
}

print("\n📦 Package Check:")
all_good = True
for package, description in packages.items():
    try:
        mod = importlib.import_module(package)
        version = getattr(mod, "__version__", "installed")
        print(f"   ✅ {package:<15} {version:<12} → {description}")
    except ImportError:
        print(f"   ❌ {package:<15} NOT FOUND    → {description}")
        all_good = False

# ── Folder structure check ────────────────────────────
import os
print("\n📁 Folder Structure Check:")
required_folders = [
    "data/raw", "data/processed", "data/quarantine",
    "logs", "ingestion", "db", "kpi",
    "api", "dashboard", "ai", "scripts"
]
for folder in required_folders:
    exists = os.path.exists(folder)
    icon = "✅" if exists else "❌"
    print(f"   {icon} {folder}")

# ── .env check ────────────────────────────────────────
print("\n🔐 Environment File Check:")
env_exists = os.path.exists(".env")
print(f"   {'✅' if env_exists else '❌'} .env file")
gitignore_exists = os.path.exists(".gitignore")
print(f"   {'✅' if gitignore_exists else '❌'} .gitignore file")

# ── Final verdict ─────────────────────────────────────
print("\n" + "=" * 55)
if all_good:
    print("  🎉 SETUP COMPLETE — Ready for Phase 2!")
else:
    print("  ⚠️  Some packages missing — paste errors above")
print("=" * 55 + "\n")