import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils.database import DatabaseManager
from utils.auth import authenticate_user
from utils.helpers import format_currency, get_dashboard_metrics
from config.settings import APP_CONFIG

# Page configuration
st.set_page_config(
    page_title="EduCRM - Coaching Institute Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    authenticate_user()
    if not st.session_state.authenticated:
        st.stop()

# Main Dashboard
st.title("🎓 EduCRM Dashboard")
st.markdown("Welcome back! Here's what's happening at your institute.")

# Last updated timestamp
st.caption(f"Last updated: {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}")

# Get dashboard metrics
try:
    metrics = get_dashboard_metrics(db)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Students",
            value=metrics['total_students'],
            delta=f"+{metrics['student_growth']}% vs last month"
        )
    
    with col2:
        st.metric(
            label="Active Batches",
            value=metrics['active_batches'],
            delta=f"+{metrics['batch_growth']} vs last month"
        )
    
    with col3:
        st.metric(
            label="Monthly Revenue",
            value=format_currency(metrics['monthly_revenue']),
            delta=f"+{metrics['revenue_growth']}% vs last month"
        )
    
    with col4:
        st.metric(
            label="Pending Fees",
            value=format_currency(metrics['pending_fees']),
            delta=f"{metrics['pending_count']} students"
        )
    
    # Charts and Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Student Distribution by Category")
        category_data = db.get_category_distribution()
        if not category_data.empty:
            fig = px.pie(
                category_data, 
                values='student_count', 
                names='category_name',
                title="Students by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No student data available yet.")
    
    with col2:
        st.subheader("💰 Monthly Fee Collection")
        fee_data = db.get_monthly_fee_data()
        if not fee_data.empty:
            fig = px.bar(
                fee_data, 
                x='month', 
                y='amount',
                title="Fee Collection Trend"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No fee collection data available yet.")
    
    # Recent Activities
    st.subheader("📋 Recent Activities")
    activities = db.get_recent_activities()
    if not activities.empty:
        for _, activity in activities.head(5).iterrows():
            st.write(f"• {activity['description']}")
            st.caption(f"{activity['time_ago']}")
    else:
        st.info("No recent activities to display.")
    
    # Pending Tasks
    st.subheader("⚠️ Pending Tasks")
    
    # Fee reminders
    pending_fees = db.get_pending_fees()
    if not pending_fees.empty:
        st.warning(f"**Collect pending fees from {len(pending_fees)} students** - Due: Today")
    
    # Batch schedules
    upcoming_batches = db.get_upcoming_batches()
    if not upcoming_batches.empty:
        st.info(f"**{len(upcoming_batches)} batches starting this week** - Due: This week")
    
    # Categories Overview
    st.subheader("📚 Categories Overview")
    categories = db.get_categories_overview()
    
    if not categories.empty:
        for _, category in categories.iterrows():
            with st.expander(f"**{category['name']}** - {category['description']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Students", category['student_count'])
                with col2:
                    st.metric("Batches", category['batch_count'])
                with col3:
                    st.metric("Revenue", format_currency(category['revenue']))
    else:
        st.info("No categories configured yet. Please add categories to get started.")

except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}")
    st.info("Please check your database connection and try again.")

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=EduCRM", caption="Coaching Institute CRM")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    if st.button("➕ Add New Student", use_container_width=True):
        st.switch_page("pages/1_Student_Management.py")
    
    if st.button("📱 Send WhatsApp", use_container_width=True):
        st.switch_page("pages/3_Communication.py")
    
    if st.button("💳 Fee Management", use_container_width=True):
        st.switch_page("pages/4_Fee_Management.py")
    
    st.markdown("---")
    st.markdown("### Database Status")
    
    try:
        db_status = db.check_connection()
        if db_status:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Disconnected")
    except Exception as e:
        st.error("❌ Database Error")
