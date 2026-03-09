# Interface for starting FluffyApp and selecting between pages
import streamlit as st

st.write("Welcome to FluffyApp! Please select a page from the sidebar to get started.")
# Page navigation
pages = [
    st.Page("pages/Ceres6App/1_Ceres6_Search.py", "Ceres6 Search"),
    st.Page("pages/MemberOrderTrendsApp/2_app.py", "Member Order Trends")
]

# Add pages to sidebar
pg = st.navigation(pages, position="sidebar", expandable= True)

pg.run()