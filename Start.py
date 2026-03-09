# Interface for starting FluffyApp and selecting between pages
import streamlit as st

st.set_page_config(
    page_title="FluffyApp", 
    page_icon="🥑", 
    layout="wide")

st.write("Welcome to FluffyApp! Please select a page from the sidebar to get started.")

st.markdown("""
FluffyApp is an all-in one interface specifically for Feeding San Diego. It currently has two main features:
1. Ceres6 Query Tool: A user-friendly interface for querying the Ceres6 database, allowing users to locate 
    specific information in reports about food distribution, member organizations, and more.
2. Member Distribution Trends: A tool for visualizing and analyzing trends in member or regional distribution over time.
    You also have the option to download a copy of the report for further analysis.
"""
)

# Page navigation
pages = [
    st.Page("pages/Ceres6App/1_Ceres6_Search.py",  title =   "Ceres6 Query Tool"),
    st.Page("pages/MemberOrderTrendsApp/2_Order_Trends.py", title =   "Member Distribution Trends")
]

# Add pages to sidebar
pg = st.navigation(pages)

pg.run()