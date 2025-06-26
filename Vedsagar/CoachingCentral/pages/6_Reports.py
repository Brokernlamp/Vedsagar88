import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from utils.database import DatabaseManager
from utils.helpers import format_currency, format_date

st.set_page_config(page_title="Reports & Analytics", page_icon="📊", layout="wide")

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page first.")
    st.stop()

st.title("📊 Reports & Analytics")

# Tabs for different report categories
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Dashboard Reports", "👥 Student Reports", "💰 Financial Reports", "📚 Academic Reports", "🔧 System Reports"])

with tab1:
    st.subheader("📈 Executive Dashboard Reports")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Report Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Report End Date", value=date.today())
    
    if st.button("Generate Dashboard Report", type="primary"):
        try:
            # Key Performance Indicators
            st.subheader("🎯 Key Performance Indicators")
            
            kpi_data = db.get_kpi_data(start_date, end_date)
            
            if kpi_data:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Revenue",
                        format_currency(kpi_data.get('total_revenue', 0)),
                        delta=f"{kpi_data.get('revenue_change', 0)}% vs previous period"
                    )
                
                with col2:
                    st.metric(
                        "New Enrollments",
                        kpi_data.get('new_enrollments', 0),
                        delta=f"{kpi_data.get('enrollment_change', 0)}% vs previous period"
                    )
                
                with col3:
                    st.metric(
                        "Collection Rate",
                        f"{kpi_data.get('collection_rate', 0):.1f}%",
                        delta=f"{kpi_data.get('collection_change', 0)}% vs target"
                    )
                
                with col4:
                    st.metric(
                        "Average Performance",
                        f"{kpi_data.get('avg_performance', 0):.1f}%",
                        delta=f"{kpi_data.get('performance_change', 0)}% vs previous period"
                    )
            
            # Revenue and Enrollment Trends
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Revenue Trend")
                revenue_data = db.get_revenue_trend_data(start_date, end_date)
                
                if not revenue_data.empty:
                    fig = px.line(
                        revenue_data,
                        x='date',
                        y='revenue',
                        title="Daily Revenue Collection",
                        markers=True
                    )
                    fig.update_layout(yaxis_title="Revenue (₹)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No revenue data available for the selected period.")
            
            with col2:
                st.subheader("👥 Enrollment Trend")
                enrollment_data = db.get_enrollment_trend_data(start_date, end_date)
                
                if not enrollment_data.empty:
                    fig = px.bar(
                        enrollment_data,
                        x='date',
                        y='new_enrollments',
                        title="Daily New Enrollments"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No enrollment data available for the selected period.")
            
            # Category Performance Overview
            st.subheader("📚 Category Performance Overview")
            category_performance = db.get_category_performance_summary(start_date, end_date)
            
            if not category_performance.empty:
                # Performance comparison chart
                fig = px.bar(
                    category_performance,
                    x='category',
                    y=['avg_performance', 'collection_rate', 'enrollment_rate'],
                    title="Category Performance Comparison",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed table
                st.dataframe(
                    category_performance,
                    use_container_width=True,
                    column_config={
                        "avg_performance": st.column_config.NumberColumn("Avg Performance", format="%.1f%%"),
                        "collection_rate": st.column_config.NumberColumn("Collection Rate", format="%.1f%%"),
                        "total_revenue": st.column_config.NumberColumn("Revenue", format="₹%.0f")
                    }
                )
            
            # Export dashboard report
            if st.button("📊 Export Dashboard Report"):
                excel_data = db.export_dashboard_report(start_date, end_date)
                st.download_button(
                    label="Download Dashboard Report",
                    data=excel_data,
                    file_name=f"dashboard_report_{start_date}_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error generating dashboard report: {str(e)}")

with tab2:
    st.subheader("👥 Student Management Reports")
    
    # Report type selection
    student_report_type = st.selectbox(
        "Select Student Report Type",
        [
            "Student Demographics Report",
            "Enrollment Analysis",
            "Attendance Report", 
            "Student Performance Summary",
            "Dropout Analysis",
            "Fee Payment History"
        ]
    )
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = db.get_categories()
        category_filter = st.selectbox(
            "Filter by Category",
            ["All Categories"] + (categories['name'].tolist() if not categories.empty else [])
        )
    
    with col2:
        if category_filter != "All Categories":
            batches = db.get_batches_by_category(category_filter)
            batch_filter = st.selectbox(
                "Filter by Batch",
                ["All Batches"] + (batches['name'].tolist() if not batches.empty else [])
            )
        else:
            batch_filter = st.selectbox("Filter by Batch", ["All Batches"])
    
    with col3:
        date_range = st.selectbox(
            "Date Range",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
        )
    
    if st.button("Generate Student Report"):
        try:
            if student_report_type == "Student Demographics Report":
                st.subheader("👥 Student Demographics")
                
                demographics = db.get_student_demographics(category_filter, batch_filter)
                
                if not demographics.empty:
                    # Age distribution
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'age_group' in demographics.columns:
                            age_dist = demographics['age_group'].value_counts()
                            fig = px.pie(
                                values=age_dist.values,
                                names=age_dist.index,
                                title="Age Distribution"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        category_dist = demographics['category'].value_counts()
                        fig = px.bar(
                            x=category_dist.index,
                            y=category_dist.values,
                            title="Students by Category"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary statistics
                    st.subheader("📊 Summary Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Students", len(demographics))
                    with col2:
                        st.metric("Active Students", len(demographics[demographics['status'] == 'Active']))
                    with col3:
                        avg_age = demographics['age'].mean() if 'age' in demographics.columns else 0
                        st.metric("Average Age", f"{avg_age:.1f} years")
                    with col4:
                        male_count = len(demographics[demographics['gender'] == 'Male']) if 'gender' in demographics.columns else 0
                        st.metric("Male/Female Ratio", f"{male_count}:{len(demographics) - male_count}")
            
            elif student_report_type == "Enrollment Analysis":
                st.subheader("📈 Enrollment Analysis")
                
                enrollment_data = db.get_enrollment_analysis(category_filter, batch_filter, date_range)
                
                if not enrollment_data.empty:
                    # Monthly enrollment trend
                    monthly_enrollments = enrollment_data.groupby('month').size().reset_index(name='count')
                    
                    fig = px.line(
                        monthly_enrollments,
                        x='month',
                        y='count',
                        title="Monthly Enrollment Trend",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Enrollment by source
                    if 'enrollment_source' in enrollment_data.columns:
                        source_data = enrollment_data['enrollment_source'].value_counts()
                        fig = px.pie(
                            values=source_data.values,
                            names=source_data.index,
                            title="Enrollment Sources"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif student_report_type == "Attendance Report":
                st.subheader("📅 Attendance Analysis")
                
                attendance_data = db.get_attendance_report(category_filter, batch_filter, date_range)
                
                if not attendance_data.empty:
                    # Overall attendance statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_attendance = attendance_data['attendance_rate'].mean()
                        st.metric("Average Attendance", f"{avg_attendance:.1f}%")
                    
                    with col2:
                        high_attendance = len(attendance_data[attendance_data['attendance_rate'] >= 90])
                        st.metric("High Attendance (≥90%)", high_attendance)
                    
                    with col3:
                        low_attendance = len(attendance_data[attendance_data['attendance_rate'] < 75])
                        st.metric("Low Attendance (<75%)", low_attendance)
                    
                    # Attendance distribution
                    fig = px.histogram(
                        attendance_data,
                        x='attendance_rate',
                        nbins=10,
                        title="Attendance Rate Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Students with low attendance
                    if low_attendance > 0:
                        st.subheader("⚠️ Students with Low Attendance")
                        low_attendance_students = attendance_data[attendance_data['attendance_rate'] < 75]
                        st.dataframe(
                            low_attendance_students[['student_name', 'batch', 'attendance_rate']],
                            use_container_width=True
                        )
            
            # Export functionality
            if st.button(f"📊 Export {student_report_type}"):
                excel_data = db.export_student_report(student_report_type, category_filter, batch_filter, date_range)
                st.download_button(
                    label=f"Download {student_report_type}",
                    data=excel_data,
                    file_name=f"{student_report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error generating student report: {str(e)}")

with tab3:
    st.subheader("💰 Financial Reports")
    
    # Financial report types
    financial_report_type = st.selectbox(
        "Select Financial Report Type",
        [
            "Revenue Analysis",
            "Fee Collection Report", 
            "Outstanding Dues Report",
            "Payment Method Analysis",
            "Refund Analysis",
            "Profit & Loss Statement"
        ]
    )
    
    # Date range for financial reports
    col1, col2 = st.columns(2)
    with col1:
        fin_start_date = st.date_input("From Date", value=date.today() - timedelta(days=90), key="fin_start")
    with col2:
        fin_end_date = st.date_input("To Date", value=date.today(), key="fin_end")
    
    if st.button("Generate Financial Report"):
        try:
            if financial_report_type == "Revenue Analysis":
                st.subheader("💰 Revenue Analysis")
                
                revenue_data = db.get_detailed_revenue_analysis(fin_start_date, fin_end_date)
                
                if revenue_data:
                    # Key financial metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Revenue", format_currency(revenue_data['total_revenue']))
                    with col2:
                        st.metric("Monthly Average", format_currency(revenue_data['monthly_average']))
                    with col3:
                        st.metric("Growth Rate", f"{revenue_data['growth_rate']:.1f}%")
                    with col4:
                        st.metric("Collection Efficiency", f"{revenue_data['collection_efficiency']:.1f}%")
                    
                    # Revenue breakdown charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'category_revenue' in revenue_data:
                            fig = px.pie(
                                revenue_data['category_revenue'],
                                values='revenue',
                                names='category',
                                title="Revenue by Category"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        if 'monthly_revenue' in revenue_data:
                            fig = px.line(
                                revenue_data['monthly_revenue'],
                                x='month',
                                y='revenue',
                                title="Monthly Revenue Trend",
                                markers=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
            
            elif financial_report_type == "Fee Collection Report":
                st.subheader("💳 Fee Collection Analysis")
                
                collection_data = db.get_fee_collection_analysis(fin_start_date, fin_end_date)
                
                if collection_data:
                    # Collection summary
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Collected", format_currency(collection_data['total_collected']))
                    with col2:
                        st.metric("Collection Rate", f"{collection_data['collection_rate']:.1f}%")
                    with col3:
                        st.metric("Pending Amount", format_currency(collection_data['pending_amount']))
                    
                    # Collection trend
                    if 'daily_collection' in collection_data:
                        fig = px.bar(
                            collection_data['daily_collection'],
                            x='date',
                            y='amount',
                            title="Daily Fee Collection"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Payment method breakdown
                    if 'payment_methods' in collection_data:
                        fig = px.pie(
                            collection_data['payment_methods'],
                            values='amount',
                            names='method',
                            title="Collection by Payment Method"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif financial_report_type == "Outstanding Dues Report":
                st.subheader("⚠️ Outstanding Dues Analysis")
                
                dues_data = db.get_outstanding_dues_analysis()
                
                if dues_data:
                    # Dues summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Outstanding", format_currency(dues_data['total_outstanding']))
                    with col2:
                        st.metric("Students with Dues", dues_data['students_with_dues'])
                    with col3:
                        st.metric("Average Due Amount", format_currency(dues_data['average_due']))
                    with col4:
                        st.metric("Overdue (>30 days)", dues_data['overdue_count'])
                    
                    # Aging analysis
                    if 'aging_data' in dues_data:
                        fig = px.bar(
                            dues_data['aging_data'],
                            x='age_bucket',
                            y='amount',
                            title="Dues Aging Analysis"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Top defaulters
                    if 'top_defaulters' in dues_data:
                        st.subheader("🔴 Top Defaulters")
                        st.dataframe(
                            dues_data['top_defaulters'],
                            use_container_width=True,
                            column_config={
                                "outstanding_amount": st.column_config.NumberColumn("Outstanding", format="₹%.0f"),
                                "days_overdue": st.column_config.NumberColumn("Days Overdue")
                            }
                        )
            
            # Export financial report
            if st.button(f"📊 Export {financial_report_type}"):
                excel_data = db.export_financial_report(financial_report_type, fin_start_date, fin_end_date)
                st.download_button(
                    label=f"Download {financial_report_type}",
                    data=excel_data,
                    file_name=f"{financial_report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error generating financial report: {str(e)}")

with tab4:
    st.subheader("📚 Academic Performance Reports")
    
    # Academic report types
    academic_report_type = st.selectbox(
        "Select Academic Report Type",
        [
            "Overall Performance Analysis",
            "Subject-wise Performance",
            "Test Analysis Report",
            "Student Progress Tracking",
            "Batch Comparison Report",
            "Top Performers Report"
        ]
    )
    
    # Academic filters
    col1, col2 = st.columns(2)
    with col1:
        academic_category = st.selectbox(
            "Category",
            ["All Categories"] + (categories['name'].tolist() if not categories.empty else []),
            key="academic_category"
        )
    with col2:
        academic_period = st.selectbox(
            "Time Period",
            ["Last Month", "Last Quarter", "Last 6 Months", "Academic Year", "All Time"]
        )
    
    if st.button("Generate Academic Report"):
        try:
            if academic_report_type == "Overall Performance Analysis":
                st.subheader("📊 Overall Performance Analysis")
                
                performance_data = db.get_overall_performance_analysis(academic_category, academic_period)
                
                if performance_data:
                    # Performance metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Average Score", f"{performance_data['average_score']:.1f}%")
                    with col2:
                        st.metric("Top Score", f"{performance_data['top_score']:.1f}%")
                    with col3:
                        st.metric("Pass Rate", f"{performance_data['pass_rate']:.1f}%")
                    with col4:
                        st.metric("Tests Conducted", performance_data['total_tests'])
                    
                    # Performance distribution
                    if 'score_distribution' in performance_data:
                        fig = px.histogram(
                            performance_data['score_distribution'],
                            x='score_range',
                            y='student_count',
                            title="Score Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Performance trends
                    if 'monthly_trends' in performance_data:
                        fig = px.line(
                            performance_data['monthly_trends'],
                            x='month',
                            y='average_score',
                            title="Monthly Performance Trend",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif academic_report_type == "Subject-wise Performance":
                st.subheader("📖 Subject-wise Performance Analysis")
                
                subject_data = db.get_subject_wise_performance(academic_category, academic_period)
                
                if not subject_data.empty:
                    # Subject performance comparison
                    fig = px.bar(
                        subject_data,
                        x='subject',
                        y='average_score',
                        title="Average Performance by Subject"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed subject table
                    st.dataframe(
                        subject_data,
                        use_container_width=True,
                        column_config={
                            "average_score": st.column_config.NumberColumn("Avg Score", format="%.1f%%"),
                            "top_score": st.column_config.NumberColumn("Top Score", format="%.1f%%"),
                            "pass_rate": st.column_config.NumberColumn("Pass Rate", format="%.1f%%")
                        }
                    )
            
            elif academic_report_type == "Test Analysis Report":
                st.subheader("📝 Test Analysis Report")
                
                test_analysis = db.get_test_analysis_report(academic_category, academic_period)
                
                if test_analysis:
                    # Test statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Tests", test_analysis['total_tests'])
                    with col2:
                        st.metric("Average Participation", f"{test_analysis['avg_participation']:.1f}%")
                    with col3:
                        st.metric("Tests per Month", f"{test_analysis['tests_per_month']:.1f}")
                    
                    # Test difficulty analysis
                    if 'difficulty_analysis' in test_analysis:
                        fig = px.scatter(
                            test_analysis['difficulty_analysis'],
                            x='max_marks',
                            y='average_score',
                            size='student_count',
                            hover_name='test_name',
                            title="Test Difficulty vs Performance"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif academic_report_type == "Top Performers Report":
                st.subheader("🏆 Top Performers Report")
                
                top_performers = db.get_top_performers_report(academic_category, academic_period)
                
                if not top_performers.empty:
                    # Top 10 performers
                    st.subheader("🥇 Top 10 Students Overall")
                    
                    top_10 = top_performers.head(10)
                    
                    # Create a ranking chart
                    fig = px.bar(
                        top_10,
                        x='student_name',
                        y='average_score',
                        title="Top 10 Students by Average Score"
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed top performers table
                    st.dataframe(
                        top_10,
                        use_container_width=True,
                        column_config={
                            "average_score": st.column_config.NumberColumn("Avg Score", format="%.1f%%"),
                            "tests_taken": st.column_config.NumberColumn("Tests Taken"),
                            "consistency": st.column_config.NumberColumn("Consistency", format="%.1f")
                        }
                    )
                    
                    # Category-wise toppers
                    if academic_category == "All Categories":
                        st.subheader("🎯 Category-wise Toppers")
                        category_toppers = db.get_category_wise_toppers(academic_period)
                        
                        if not category_toppers.empty:
                            st.dataframe(
                                category_toppers,
                                use_container_width=True,
                                column_config={
                                    "score": st.column_config.NumberColumn("Score", format="%.1f%%")
                                }
                            )
            
            # Export academic report
            if st.button(f"📊 Export {academic_report_type}"):
                excel_data = db.export_academic_report(academic_report_type, academic_category, academic_period)
                st.download_button(
                    label=f"Download {academic_report_type}",
                    data=excel_data,
                    file_name=f"{academic_report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error generating academic report: {str(e)}")

with tab5:
    st.subheader("🔧 System Reports")
    
    # System report types
    system_report_type = st.selectbox(
        "Select System Report Type",
        [
            "User Activity Report",
            "Database Health Report",
            "Communication Log Report",
            "System Usage Analytics",
            "Error Log Report",
            "Backup Status Report"
        ]
    )
    
    if st.button("Generate System Report"):
        try:
            if system_report_type == "User Activity Report":
                st.subheader("👤 User Activity Report")
                
                activity_data = db.get_user_activity_report()
                
                if activity_data:
                    # Activity metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Sessions", activity_data['total_sessions'])
                    with col2:
                        st.metric("Average Session Duration", f"{activity_data['avg_duration']} min")
                    with col3:
                        st.metric("Peak Usage Hour", f"{activity_data['peak_hour']}:00")
                    
                    # Activity timeline
                    if 'daily_activity' in activity_data:
                        fig = px.line(
                            activity_data['daily_activity'],
                            x='date',
                            y='session_count',
                            title="Daily System Usage",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif system_report_type == "Database Health Report":
                st.subheader("🗄️ Database Health Report")
                
                db_health = db.get_database_health_report()
                
                if db_health:
                    # Database metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Records", db_health['total_records'])
                    with col2:
                        st.metric("Database Size", f"{db_health['db_size_mb']:.1f} MB")
                    with col3:
                        status_color = "🟢" if db_health['connection_status'] == 'Healthy' else "🔴"
                        st.metric("Connection Status", f"{status_color} {db_health['connection_status']}")
                    with col4:
                        st.metric("Last Backup", db_health['last_backup'])
                    
                    # Table-wise record counts
                    if 'table_stats' in db_health:
                        fig = px.bar(
                            db_health['table_stats'],
                            x='table_name',
                            y='record_count',
                            title="Records by Table"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif system_report_type == "Communication Log Report":
                st.subheader("📱 Communication Log Report")
                
                comm_logs = db.get_communication_log_report()
                
                if comm_logs:
                    # Communication metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Messages Sent", comm_logs['total_messages'])
                    with col2:
                        st.metric("This Month", comm_logs['messages_this_month'])
                    with col3:
                        st.metric("Success Rate", f"{comm_logs['success_rate']:.1f}%")
                    
                    # Message trends
                    if 'daily_messages' in comm_logs:
                        fig = px.bar(
                            comm_logs['daily_messages'],
                            x='date',
                            y='message_count',
                            title="Daily Message Volume"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Template usage
                    if 'template_usage' in comm_logs:
                        fig = px.pie(
                            comm_logs['template_usage'],
                            values='usage_count',
                            names='template_name',
                            title="Template Usage Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            elif system_report_type == "System Usage Analytics":
                st.subheader("📈 System Usage Analytics")
                
                usage_data = db.get_system_usage_analytics()
                
                if usage_data:
                    # Usage metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Daily Active Users", usage_data['daily_active_users'])
                    with col2:
                        st.metric("Most Used Feature", usage_data['top_feature'])
                    with col3:
                        st.metric("Average Response Time", f"{usage_data['avg_response_time']} ms")
                    with col4:
                        st.metric("System Uptime", f"{usage_data['uptime_percentage']:.1f}%")
                    
                    # Feature usage
                    if 'feature_usage' in usage_data:
                        fig = px.bar(
                            usage_data['feature_usage'],
                            x='feature_name',
                            y='usage_count',
                            title="Feature Usage Statistics"
                        )
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Export system report
            if st.button(f"📊 Export {system_report_type}"):
                excel_data = db.export_system_report(system_report_type)
                st.download_button(
                    label=f"Download {system_report_type}",
                    data=excel_data,
                    file_name=f"{system_report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error generating system report: {str(e)}")
    
    # Quick system health check
    st.subheader("⚡ Quick System Health Check")
    
    if st.button("Run Health Check"):
        try:
            health_status = db.run_system_health_check()
            
            if health_status:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    db_status = "✅ Healthy" if health_status['database'] else "❌ Issues"
                    st.metric("Database", db_status)
                
                with col2:
                    api_status = "✅ Healthy" if health_status.get('api_connection', True) else "❌ Issues"
                    st.metric("API Connection", api_status)
                
                with col3:
                    storage_status = "✅ Healthy" if health_status.get('storage', True) else "❌ Issues"
                    st.metric("Storage", storage_status)
                
                with col4:
                    performance_status = "✅ Good" if health_status.get('performance', True) else "⚠️ Slow"
                    st.metric("Performance", performance_status)
                
                # Recommendations
                if 'recommendations' in health_status and health_status['recommendations']:
                    st.subheader("💡 System Recommendations")
                    for recommendation in health_status['recommendations']:
                        st.info(f"• {recommendation}")
        
        except Exception as e:
            st.error(f"Error running health check: {str(e)}")

# Bulk report generation
st.markdown("---")
st.subheader("📋 Bulk Report Generation")

col1, col2 = st.columns(2)

with col1:
    st.write("**Generate Multiple Reports**")
    selected_reports = st.multiselect(
        "Select reports to generate",
        [
            "Dashboard Summary",
            "Student Demographics",
            "Financial Summary", 
            "Academic Performance",
            "Fee Collection Status",
            "Communication Logs"
        ]
    )

with col2:
    st.write("**Report Format**")
    report_format = st.radio("Output Format", ["Excel (.xlsx)", "PDF Report", "CSV Files"])
    
    if st.button("Generate Selected Reports", type="primary"):
        if selected_reports:
            try:
                # Generate bulk reports
                with st.spinner("Generating reports..."):
                    bulk_data = db.generate_bulk_reports(selected_reports, report_format)
                
                if bulk_data:
                    st.success(f"✅ Generated {len(selected_reports)} reports successfully!")
                    
                    # Provide download link
                    st.download_button(
                        label="📊 Download Bulk Reports",
                        data=bulk_data,
                        file_name=f"bulk_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("Failed to generate bulk reports.")
            
            except Exception as e:
                st.error(f"Error generating bulk reports: {str(e)}")
        else:
            st.warning("Please select at least one report to generate.")
