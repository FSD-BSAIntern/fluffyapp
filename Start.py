# Interface for starting FluffyApp and selecting between pages
import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
ceres6_page = st.Page("pages/Ceres6App/1_Ceres6_Search.py",  title =   "Ceres6 Query Tool")
order_trends_page = st.Page("pages/MemberOrderTrendsApp/2_Order_Trends.py", title =   "Member Distribution Trends")
hompage_page = st.Page("pages/Home.py", title="Home", icon=":material/house:")

if st.session_state.logged_in:
    pg = st.navigation([hompage_page, ceres6_page, order_trends_page, logout_page])
    
else:    
    pg = st.navigation([hompage_page, login_page])

pg.run()