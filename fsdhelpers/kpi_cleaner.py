from __future__ import annotations
from pathlib import Path
import pandas as pd

from . import config

def _make_order_key(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
    )

def load_orders(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        path = config.ORDERS_FILE
    return pd.read_csv(path, encoding="latin-1")

def load_weights(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        path = config.WEIGHTS_FILE
    return pd.read_csv(path, encoding="latin-1")

def load_qclog(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        path = config.QCLOG_FILE
    return pd.read_csv(path, encoding="latin-1" )

orders  = load_orders()
weights = load_weights()
qclog   = load_qclog()

def clean_weights_df(weights: pd.DataFrame) -> pd.DataFrame:
    weights_df = weights.copy()

    weights_df["Quantity"] = (
        weights_df["Quantity"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"[^\d.-]", "", regex=True)
    )
    weights_df["Quantity"] = pd.to_numeric(weights_df["Quantity"], errors="coerce")

    weights_df["Gross Weight"] = (
        weights_df["Gross Weight"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    weights_df["Gross Weight"] = pd.to_numeric(weights_df["Gross Weight"], errors="coerce")

    weights_df["order_key"] = weights_df["Document No"].astype(str).str.extract(r"([A-Za-z]+-\d+)")[0]

    drop_cols = ["Fiscal Year", "Fiscal Month", "Fiscal Quarter", "Document No"]
    weights_df = weights_df.drop(columns=[c for c in drop_cols if c in weights_df.columns])

    weights_df = weights_df[weights_df["FBC Product Type Code"] != 28]

    weights_df = (
        weights_df.groupby("order_key", dropna=False)
        .agg(
            Gross_Weight=("Gross Weight", "sum"),
            Shipment_Date=("Date", "first"),
            Agency_Name=("Bill-to Agency", "first"),
            FBC_Product_Type_Code=("FBC Product Type Code", "first"),
            Total_Cases=("Quantity", "sum"),
        )
        .reset_index()
    )

    return weights_df


def clean_orders_df(orders: pd.DataFrame) -> pd.DataFrame:
    cleaned_orders = orders.copy()

    cleaned_orders["Date"] = cleaned_orders["Date"].ffill()
    cleaned_orders["Order Number"] = cleaned_orders["Order Number"].ffill()
    cleaned_orders["Agency Name"] = cleaned_orders["Agency Name"].ffill()

    cleaned_orders = cleaned_orders[
        ~(
            cleaned_orders["Order Number"].isna()
            | (cleaned_orders["Type"].isna() & cleaned_orders["#Pallets"].isna())
        )
    ].reset_index(drop=True)

    cleaned_orders["order_key"] = _make_order_key(cleaned_orders["Order Number"])
    return cleaned_orders


def clean_qc_log_df(qclog: pd.DataFrame) -> pd.DataFrame:
    cleaned_qc_log = qclog.copy()

    cleaned_qc_log = cleaned_qc_log[
        ~(cleaned_qc_log["Shipment Date"].isna() & cleaned_qc_log["Agency Order #"].isna())
    ]
    cleaned_qc_log["Shipment Date"] = cleaned_qc_log["Shipment Date"].ffill()
    cleaned_qc_log["order_key"] = _make_order_key(cleaned_qc_log["Agency Order #"])

    return cleaned_qc_log.reset_index(drop=True)


def build_master_dataset(
    orders: pd.DataFrame,
    qclog: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    cleaned_orders = clean_orders_df(orders)
    cleaned_qc_log = clean_qc_log_df(qclog)
    weights_df = clean_weights_df(weights)

    merged_data = cleaned_orders.merge(cleaned_qc_log, on="order_key", how="inner")
    merged_data = merged_data.merge(weights_df, on="order_key", how="inner")

    master = merged_data.copy()

    drop_cols = ["Agency Order #", "Date", "Agency Name_y"]
    master = master.drop(columns=[c for c in drop_cols if c in master.columns])

    master = master.rename(columns={
        "Agency Name_x": "Agency Name",
        "Done_x": "Order Completed",
        "Done_y": "QC Audit Completed",
        "Type": "Product Type",
        "#Pallets": "No. of Pallets",
        "Team Member_x": "Team Member (Whiteboard)",
        "Team Member_y": "Team Member (QC Log)",
        "Item #": "QC Item No.",
        "Quantity Pulled": "Case Quantity Pulled",
        "Agency Order Total": "Total Cases Ordered",
        "Checked By": "Audited By",
    })

    master["No. of Pallets"] = pd.to_numeric(master["No. of Pallets"], errors="coerce")
    master["Shipment Date"] = pd.to_datetime(master["Shipment Date"], errors="coerce")

    master = master[master["Shipment Date"] < pd.Timestamp("2025-11-16")].reset_index(drop=True)

    return master

def load_and_build_master() -> pd.DataFrame:
    orders = load_orders()
    qclog = load_qclog()
    weights = load_weights()
    return build_master_dataset(orders, qclog, weights)