from pathlib import Path

# config.py
DATA_PATH = r"O:\Business Systems Analyst\Projects\CC_Isaiah De La Rosa\Program Tier Cost Project\PCMapp\ProgramDistribution-idlrOG.csv"

# Column names expected in the dataset (exact, case-sensitive).
COL_DATE = "Date"
COL_FISCAL_YEAR = "Fiscal Year"
COL_BILL_TO_AGENCY = "Bill-to Agency"
COL_REGION = "Geographical Location Code"
COL_HH_CODE = "FBC Size Code"
COL_GROSS_WEIGHT = "Gross Weight"

# Optional columns (used only for display / future filters)
COL_CITY = "City"
COL_ZIP = "ZIP Code"

# HH buckets
HH_BUCKETS = [
    ("XS", 1, 50),
    ("S", 51, 150),
    ("M", 151, 300),
    ("L", 301, 600),
    ("XL", 601, float("inf")),
]

# --- KPI Showcase ---

ROOT_DIR = Path(__file__).resolve().parents[1]  # Assuming this file is in fsdhelpers
KPI_DATA_DIR = ROOT_DIR / "pages" / "KPIApp" / "data"

ORDERS_FILE = KPI_DATA_DIR / "Order Fulfillment Whiteboard (Current).csv"
WEIGHTS_FILE = KPI_DATA_DIR / "OrderGrossWeightsUpdated.csv"
QCLOG_FILE = KPI_DATA_DIR / "Quality Control Log.csv"