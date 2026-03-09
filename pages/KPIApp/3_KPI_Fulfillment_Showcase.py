import streamlit as st
import pandas as pd

import streamlit as st
from fsdhelpers.kpi_cleaner import (
    load_orders, load_qclog, load_weights,
    clean_orders_df, clean_qc_log_df, clean_weights_df
)
from fsdhelpers import kpi_summaries

st.title("KPI Optimization Model")

orders_raw = load_orders()
qclog_raw = load_qclog()
weights_raw = load_weights()

orders = clean_orders_df(orders_raw)
qclog = clean_qc_log_df(qclog_raw)
weights = clean_weights_df(weights_raw)

st.subheader("Join diagnostics")

st.write("Orders rows:", len(orders))
st.write("QC rows:", len(qclog))
st.write("Weights rows:", len(weights))

st.write("Orders unique keys:", orders["order_key"].nunique())
st.write("QC unique keys:", qclog["order_key"].nunique())
st.write("Weights unique keys:", weights["order_key"].nunique())

orders_keys = set(orders["order_key"].dropna())
qc_keys = set(qclog["order_key"].dropna())
weights_keys = set(weights["order_key"].dropna())

st.write("Orders ∩ QC:", len(orders_keys & qc_keys))
st.write("Orders ∩ Weights:", len(orders_keys & weights_keys))
st.write("QC ∩ Weights:", len(qc_keys & weights_keys))
st.write("Orders ∩ QC ∩ Weights:", len(orders_keys & qc_keys & weights_keys))

st.write("Sample Orders keys:", sorted(list(orders_keys))[:20])
st.write("Sample QC keys:", sorted(list(qc_keys))[:20])
st.write("Sample Weights keys:", sorted(list(weights_keys))[:20])

merged_1 = orders.merge(qclog, on="order_key", how="inner")
st.write("Rows after orders + qc merge:", len(merged_1))

merged_2 = merged_1.merge(weights, on="order_key", how="inner")
st.write("Rows after weights merge:", len(merged_2))

st.stop()

@st.cache_data
def load_master():
    return load_and_build_master()

master = load_master()

tab_model, tab_method = st.tabs(
    ["KPI Model", "Parameters & Preparation Showcase"]
)

# ----------------------------
# MAIN MODEL TAB
# ----------------------------

with tab_model:

    st.sidebar.header("Model Controls")

    master["Shipment Date"] = pd.to_datetime(master["Shipment Date"], errors="coerce")

    valid_dates = master["Shipment Date"].dropna()

    if valid_dates.empty:
        st.error("No valid Shipment Date values were found in the dataset.")
        st.stop()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    start_date = st.sidebar.date_input("Start Date", value=min_date)
    end_date = st.sidebar.date_input("End Date", value=max_date)

    period = st.sidebar.selectbox(
        "Period Level",
        ["Daily", "Weekly", "Monthly"]
    )

    view = st.sidebar.selectbox(
        "Select Analysis",
        [
            "Overall Case Movement",
            "Overall Weight Movement",
            "Overall Pallets",
            "Employee Case Movement",
            "Employee Weight Movement",
            "Employee Pallets",
            "Order Tier Distribution",
            "Pallet Effort Model (Experimental)"
        ]
    )

    mode = st.sidebar.radio(
        "View Mode",
        ["Overall", "By Employee"]
    )

    employees = master["Team Member (Whiteboard)"].dropna().unique()

    selected_employees = None

    if mode == "By Employee":

        selected_employees = st.sidebar.multiselect(
            "Select Employees",
            employees,
            default=list(employees)
        )

    filtered = kpi_summaries.filter_master(
        master,
        start_date,
        end_date,
        selected_employees
    )

    # ----------------------------
    # Render selected analysis
    # ----------------------------

    if view == "Overall Case Movement":

        df = kpi_summaries.overall_cases_summary(filtered, period)
        st.line_chart(df.set_index("Period"))

    elif view == "Overall Weight Movement":

        df = kpi_summaries.overall_weight_summary(filtered, period)
        st.line_chart(df.set_index("Period"))

    elif view == "Overall Pallets":

        df = kpi_summaries.overall_pallet_summary(filtered, period)
        st.line_chart(df.set_index("Period"))

    elif view == "Employee Case Movement":

        df = kpi_summaries.employee_cases_summary(filtered, period)
        st.dataframe(df)

    elif view == "Employee Weight Movement":

        df = kpi_summaries.employee_weight_summary(filtered, period)
        st.dataframe(df)

    elif view == "Employee Pallets":

        df = kpi_summaries.employee_pallet_summary(filtered, period)
        st.dataframe(df)

    elif view == "Order Tier Distribution":

        df = kpi_summaries.order_tier_distribution(filtered)
        st.dataframe(df)

    elif view == "Pallet Effort Model (Experimental)":

        df = kpi_summaries.pallet_effort_model(filtered)
        st.dataframe(df)


# ----------------------------
# METHODOLOGY TAB
# ----------------------------

with tab_method:

    st.header("Data Preparation & Cleaning Pipeline")

    st.markdown("""
    ### Source Datasets

    - Order Fulfillment Whiteboard  
    - Quality Control Log  
    - Order Gross Weights  

    ### Key Cleaning Steps

    **Whiteboard**
    - Forward-fill missing dates and agency names  
    - Remove incomplete order rows  

    **QC Log**
    - Remove blank records  
    - Forward-fill shipment dates  

    **Gross Weights**
    - Normalize order numbers  
    - Clean numeric fields  
    - Remove produce shipments  

    ### Merge Logic

    All datasets are merged using a normalized **Order Number key**.

    ### Feature Engineering

    - Order Size Tier model (scaled composite index)
    - Pallet Effort multiplier model
    - Employee productivity metrics
    """)

    st.subheader("Cleaned Master Dataset Preview")

    st.dataframe(master.head(50))