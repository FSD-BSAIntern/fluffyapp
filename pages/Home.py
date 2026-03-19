# Interface for starting FluffyApp and selecting between pages
import streamlit as st

st.set_page_config(
    page_title="Fluffy",
    page_icon="🥑",
    layout="wide"
)

st.title("Welcome to Fluffy! 🥑")
st.write("Please select a page from the sidebar 👈 to get started.")

st.sidebar.header("About Fluffy")

st.write("""
Fluffy is an all-in-one interface specifically for Feeding San Diego.

It currently has two main features:

**1. Ceres6 Query Tool** 🔍 \\
A user-friendly interface for querying the Ceres6 database, allowing users to locate specific information in reports about food distribution, member organizations, and more.

**2. Member Distribution Trends** 📈 \\
A tool for visualizing and analyzing trends in member or regional distribution over time. You also have the option to download a copy of the report for record-keeping.

**3. KPI Fulfillment Showcase** 🎯 \\
A prototype showcase for an archived project with Fulfillment for analyzing key performance metrics, such as daily and weekly case or pallet movement over time. The goal is for new metrics to guide future operations to continously identify pain points and improve on them.

""")
