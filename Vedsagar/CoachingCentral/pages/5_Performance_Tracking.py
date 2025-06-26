import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from utils.database import DatabaseManager
from utils.helpers import format_date

st.set_page_config(page_title="Performance Tracking", page_icon="📈", layout="wide")

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page first.")
    st.stop()

st.title("📈 Performance Tracking")

# Tabs for different performance features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Record Performance", "👤 Student Analytics", "📊 Batch Performance", "📋 Test Management", "📈 Progress Reports"])

with tab1:
    st.subheader("📝 Record Student Performance")
    
    # Test/Assessment selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Create or select test
        test_option = st.radio("Test/Assessment", ["Select Existing Test", "Create New Test"])
        
        if test_option == "Create New Test":
            with st.form("create_test_form"):
                test_name = st.text_input("Test Name *", placeholder="e.g., Unit Test 1, Mock Test")
                test_subject = st.text_input("Subject", placeholder="e.g., Physics, Chemistry, Mathematics")
                test_date = st.date_input("Test Date", value=datetime.now().date())
                max_marks = st.number_input("Total Marks", min_value=1, value=100)
                
                # Category and batch selection
                categories = db.get_categories()
                if not categories.empty:
                    test_category = st.selectbox("Category", categories['name'].tolist())
                    
                    if test_category:
                        batches = db.get_batches_by_category(test_category)
                        if not batches.empty:
                            test_batch = st.selectbox("Batch", batches['name'].tolist())
                        else:
                            st.warning("No batches found for selected category.")
                            test_batch = None
                else:
                    st.error("Please create categories and batches first.")
                    test_category = None
                    test_batch = None
                
                test_description = st.text_area("Description", placeholder="Test details, syllabus covered, etc.")
                
                if st.form_submit_button("Create Test"):
                    if test_name and test_category and test_batch:
                        try:
                            test_data = {
                                'name': test_name,
                                'subject': test_subject,
                                'date': test_date,
                                'max_marks': max_marks,
                                'category': test_category,
                                'batch': test_batch,
                                'description': test_description
                            }
                            
                            test_id = db.create_test(test_data)
                            if test_id:
                                st.success(f"✅ Test '{test_name}' created successfully!")
                                st.session_state['selected_test_id'] = test_id
                                st.rerun()
                            else:
                                st.error("Failed to create test.")
                        except Exception as e:
                            st.error(f"Error creating test: {str(e)}")
                    else:
                        st.error("Please fill all required fields.")
        
        else:  # Select existing test
            existing_tests = db.get_recent_tests()
            if not existing_tests.empty:
                selected_test = st.selectbox(
                    "Select Test",
                    existing_tests.apply(
                        lambda x: f"{x['name']} - {x['batch']} ({format_date(x['date'])})",
                        axis=1
                    ).tolist()
                )
                
                if selected_test:
                    test_index = existing_tests.apply(
                        lambda x: f"{x['name']} - {x['batch']} ({format_date(x['date'])})",
                        axis=1
                    ).tolist().index(selected_test)
                    
                    st.session_state['selected_test_id'] = existing_tests.iloc[test_index]['id']
            else:
                st.info("No tests found. Please create a test first.")
    
    with col2:
        # Performance entry
        if 'selected_test_id' in st.session_state:
            test_details = db.get_test_details(st.session_state['selected_test_id'])
            
            if test_details:
                st.info(f"**Test:** {test_details['name']}")
                st.info(f"**Batch:** {test_details['batch']}")
                st.info(f"**Max Marks:** {test_details['max_marks']}")
                
                # Get students in the test batch
                batch_students = db.get_students_by_batch_name(test_details['batch'])
                
                if not batch_students.empty:
                    # Check existing scores
                    existing_scores = db.get_test_scores(st.session_state['selected_test_id'])
                    
                    # Score entry method
                    entry_method = st.radio("Score Entry Method", ["Individual Entry", "Bulk Entry"])
                    
                    if entry_method == "Individual Entry":
                        selected_student = st.selectbox(
                            "Select Student",
                            batch_students['full_name'].tolist()
                        )
                        
                        if selected_student:
                            student_data = batch_students[batch_students['full_name'] == selected_student].iloc[0]
                            
                            # Check if score already exists
                            existing_score = existing_scores[existing_scores['student_id'] == student_data['id']]
                            current_score = existing_score['marks_obtained'].iloc[0] if not existing_score.empty else 0
                            
                            with st.form("individual_score_form"):
                                marks_obtained = st.number_input(
                                    f"Marks for {selected_student}",
                                    min_value=0,
                                    max_value=test_details['max_marks'],
                                    value=int(current_score)
                                )
                                
                                attendance = st.selectbox("Attendance", ["Present", "Absent"])
                                remarks = st.text_area("Remarks", placeholder="Optional comments about performance")
                                
                                if st.form_submit_button("Save Score"):
                                    try:
                                        score_data = {
                                            'test_id': st.session_state['selected_test_id'],
                                            'student_id': student_data['id'],
                                            'marks_obtained': marks_obtained,
                                            'attendance': attendance,
                                            'remarks': remarks
                                        }
                                        
                                        if db.save_test_score(score_data):
                                            st.success(f"✅ Score saved for {selected_student}!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to save score.")
                                    except Exception as e:
                                        st.error(f"Error saving score: {str(e)}")
                    
                    else:  # Bulk Entry
                        st.subheader("Bulk Score Entry")
                        
                        # Create a form for all students
                        with st.form("bulk_score_form"):
                            score_data = []
                            
                            for _, student in batch_students.iterrows():
                                existing_score = existing_scores[existing_scores['student_id'] == student['id']]
                                current_score = existing_score['marks_obtained'].iloc[0] if not existing_score.empty else 0
                                
                                col1, col2, col3 = st.columns([3, 2, 2])
                                
                                with col1:
                                    st.write(student['full_name'])
                                
                                with col2:
                                    marks = st.number_input(
                                        "Marks",
                                        min_value=0,
                                        max_value=test_details['max_marks'],
                                        value=int(current_score),
                                        key=f"marks_{student['id']}"
                                    )
                                
                                with col3:
                                    attendance = st.selectbox(
                                        "Attendance",
                                        ["Present", "Absent"],
                                        key=f"attendance_{student['id']}"
                                    )
                                
                                score_data.append({
                                    'student_id': student['id'],
                                    'marks': marks,
                                    'attendance': attendance
                                })
                            
                            if st.form_submit_button("Save All Scores"):
                                try:
                                    success_count = 0
                                    for score in score_data:
                                        score_entry = {
                                            'test_id': st.session_state['selected_test_id'],
                                            'student_id': score['student_id'],
                                            'marks_obtained': score['marks'],
                                            'attendance': score['attendance'],
                                            'remarks': ''
                                        }
                                        
                                        if db.save_test_score(score_entry):
                                            success_count += 1
                                    
                                    st.success(f"✅ Saved scores for {success_count} students!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error saving bulk scores: {str(e)}")
                else:
                    st.warning("No students found in the selected batch.")

with tab2:
    st.subheader("👤 Individual Student Analytics")
    
    # Student selection
    students = db.get_all_students()
    
    if not students.empty:
        selected_student = st.selectbox(
            "Select Student for Analysis",
            students.apply(lambda x: f"{x['full_name']} - {x['batch']}", axis=1).tolist()
        )
        
        if selected_student:
            student_index = students.apply(lambda x: f"{x['full_name']} - {x['batch']}", axis=1).tolist().index(selected_student)
            student_data = students.iloc[student_index]
            
            # Student performance data
            performance_data = db.get_student_performance_history(student_data['id'])
            
            if not performance_data.empty:
                # Performance metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_score = performance_data['percentage'].mean()
                    st.metric("Average Score", f"{avg_score:.1f}%")
                
                with col2:
                    total_tests = len(performance_data)
                    st.metric("Tests Taken", total_tests)
                
                with col3:
                    best_score = performance_data['percentage'].max()
                    st.metric("Best Score", f"{best_score:.1f}%")
                
                with col4:
                    attendance_rate = (performance_data['attendance'] == 'Present').mean() * 100
                    st.metric("Attendance", f"{attendance_rate:.1f}%")
                
                # Performance trend chart
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Performance Trend")
                    fig = px.line(
                        performance_data,
                        x='test_date',
                        y='percentage',
                        markers=True,
                        title=f"Performance Trend - {student_data['full_name']}"
                    )
                    fig.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("📊 Subject-wise Performance")
                    if 'subject' in performance_data.columns:
                        subject_avg = performance_data.groupby('subject')['percentage'].mean().reset_index()
                        
                        if not subject_avg.empty:
                            fig = px.bar(
                                subject_avg,
                                x='subject',
                                y='percentage',
                                title="Average Score by Subject"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Subject-wise data not available.")
                
                # Detailed performance table
                st.subheader("📋 Detailed Performance History")
                st.dataframe(
                    performance_data[[
                        'test_name', 'test_date', 'marks_obtained', 
                        'max_marks', 'percentage', 'attendance'
                    ]],
                    use_container_width=True,
                    column_config={
                        "test_date": st.column_config.DateColumn("Test Date"),
                        "percentage": st.column_config.NumberColumn("Score %", format="%.1f%%")
                    }
                )
                
                # Performance insights
                st.subheader("🎯 Performance Insights")
                
                # Trend analysis
                if len(performance_data) >= 3:
                    recent_avg = performance_data.tail(3)['percentage'].mean()
                    overall_avg = performance_data['percentage'].mean()
                    
                    if recent_avg > overall_avg + 5:
                        st.success(f"📈 **Improving Performance**: Recent average ({recent_avg:.1f}%) is significantly higher than overall average ({overall_avg:.1f}%)")
                    elif recent_avg < overall_avg - 5:
                        st.warning(f"📉 **Declining Performance**: Recent average ({recent_avg:.1f}%) is lower than overall average ({overall_avg:.1f}%)")
                    else:
                        st.info(f"📊 **Consistent Performance**: Recent performance is stable around {recent_avg:.1f}%")
                
                # Attendance insights
                if attendance_rate < 80:
                    st.error(f"⚠️ **Attendance Concern**: Student has {attendance_rate:.1f}% attendance. Consider discussing with parents.")
                elif attendance_rate >= 95:
                    st.success(f"✅ **Excellent Attendance**: Student has {attendance_rate:.1f}% attendance!")
            else:
                st.info(f"No performance data found for {student_data['full_name']}. Please record some test scores first.")
    else:
        st.warning("No students found. Please add students first.")

with tab3:
    st.subheader("📊 Batch Performance Analysis")
    
    # Batch selection
    batches = db.get_all_batches()
    
    if not batches.empty:
        selected_batch = st.selectbox(
            "Select Batch for Analysis",
            batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist()
        )
        
        if selected_batch:
            batch_index = batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist().index(selected_batch)
            batch_data = batches.iloc[batch_index]
            
            # Batch performance overview
            batch_performance = db.get_batch_performance_overview(batch_data['id'])
            
            if batch_performance:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Students", batch_performance['total_students'])
                
                with col2:
                    st.metric("Average Score", f"{batch_performance['average_score']:.1f}%")
                
                with col3:
                    st.metric("Top Score", f"{batch_performance['top_score']:.1f}%")
                
                with col4:
                    st.metric("Tests Conducted", batch_performance['total_tests'])
                
                # Performance distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Score Distribution")
                    score_distribution = db.get_batch_score_distribution(batch_data['id'])
                    
                    if not score_distribution.empty:
                        fig = px.histogram(
                            score_distribution,
                            x='percentage',
                            nbins=10,
                            title="Score Distribution in Batch"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("📈 Batch Progress Over Time")
                    batch_progress = db.get_batch_progress_over_time(batch_data['id'])
                    
                    if not batch_progress.empty:
                        fig = px.line(
                            batch_progress,
                            x='test_date',
                            y='average_percentage',
                            markers=True,
                            title="Average Score Trend"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Student ranking in batch
                st.subheader("🏆 Student Rankings")
                batch_rankings = db.get_batch_student_rankings(batch_data['id'])
                
                if not batch_rankings.empty:
                    # Add ranking
                    batch_rankings['rank'] = batch_rankings['average_score'].rank(method='dense', ascending=False).astype(int)
                    batch_rankings = batch_rankings.sort_values('rank')
                    
                    st.dataframe(
                        batch_rankings[['rank', 'student_name', 'average_score', 'tests_taken', 'attendance_rate']],
                        use_container_width=True,
                        column_config={
                            "rank": st.column_config.NumberColumn("Rank"),
                            "average_score": st.column_config.NumberColumn("Avg Score", format="%.1f%%"),
                            "attendance_rate": st.column_config.NumberColumn("Attendance", format="%.1f%%")
                        }
                    )
                
                # Performance insights for batch
                st.subheader("🎯 Batch Insights")
                
                # Identify top and struggling students
                if not batch_rankings.empty:
                    top_performers = batch_rankings.head(3)
                    struggling_students = batch_rankings[batch_rankings['average_score'] < 50]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.success("🌟 **Top Performers**")
                        for _, student in top_performers.iterrows():
                            st.write(f"• {student['student_name']} - {student['average_score']:.1f}%")
                    
                    with col2:
                        if not struggling_students.empty:
                            st.warning("⚠️ **Students Needing Attention**")
                            for _, student in struggling_students.iterrows():
                                st.write(f"• {student['student_name']} - {student['average_score']:.1f}%")
                        else:
                            st.success("✅ All students performing well!")
            else:
                st.info(f"No performance data available for batch '{batch_data['name']}'.")
    else:
        st.warning("No batches found. Please create batches first.")

with tab4:
    st.subheader("📋 Test Management")
    
    # Recent tests overview
    recent_tests = db.get_recent_tests(limit=10)
    
    if not recent_tests.empty:
        st.subheader("Recent Tests")
        
        for _, test in recent_tests.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
                
                with col1:
                    st.markdown(f"**{test['name']}**")
                    st.caption(f"{test['batch']} • {format_date(test['date'])}")
                    if test.get('subject'):
                        st.caption(f"Subject: {test['subject']}")
                
                with col2:
                    st.metric("Max Marks", test['max_marks'])
                
                with col3:
                    scores_count = db.get_test_scores_count(test['id'])
                    total_students = db.get_batch_student_count_by_name(test['batch'])
                    st.metric("Scores Entered", f"{scores_count}/{total_students}")
                
                with col4:
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("👁️", key=f"view_test_{test['id']}", help="View Results"):
                            st.session_state['view_test_results'] = test['id']
                    
                    with col_b:
                        if st.button("✏️", key=f"edit_test_{test['id']}", help="Edit Test"):
                            st.session_state['edit_test'] = test['id']
                    
                    with col_c:
                        if st.button("📊", key=f"export_test_{test['id']}", help="Export Results"):
                            try:
                                excel_data = db.export_test_results(test['id'])
                                st.download_button(
                                    label="Download Results",
                                    data=excel_data,
                                    file_name=f"test_results_{test['name']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"download_test_{test['id']}"
                                )
                            except Exception as e:
                                st.error(f"Export failed: {str(e)}")
                
                # View test results
                if st.session_state.get('view_test_results') == test['id']:
                    test_results = db.get_detailed_test_results(test['id'])
                    
                    if not test_results.empty:
                        st.subheader(f"Results: {test['name']}")
                        
                        # Test statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Average", f"{test_results['percentage'].mean():.1f}%")
                        with col2:
                            st.metric("Highest", f"{test_results['percentage'].max():.1f}%")
                        with col3:
                            st.metric("Lowest", f"{test_results['percentage'].min():.1f}%")
                        with col4:
                            pass_rate = (test_results['percentage'] >= 50).mean() * 100
                            st.metric("Pass Rate", f"{pass_rate:.1f}%")
                        
                        # Results table
                        st.dataframe(
                            test_results[['student_name', 'marks_obtained', 'max_marks', 'percentage', 'attendance']],
                            use_container_width=True,
                            column_config={
                                "percentage": st.column_config.NumberColumn("Score %", format="%.1f%%")
                            }
                        )
                    
                    if st.button("Hide Results", key=f"hide_results_{test['id']}"):
                        st.session_state['view_test_results'] = None
                        st.rerun()
                
                st.divider()
        
        # Test management actions
        st.subheader("⚙️ Test Management Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export All Test Data"):
                try:
                    excel_data = db.export_all_test_data()
                    st.download_button(
                        label="Download All Test Data",
                        data=excel_data,
                        file_name=f"all_test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        
        with col2:
            if st.button("🗑️ Archive Old Tests"):
                try:
                    archived_count = db.archive_old_tests()
                    st.success(f"Archived {archived_count} old tests.")
                except Exception as e:
                    st.error(f"Archive failed: {str(e)}")
        
        with col3:
            if st.button("📈 Generate Test Statistics"):
                st.session_state['show_test_statistics'] = True
        
        # Test statistics display
        if st.session_state.get('show_test_statistics', False):
            st.subheader("📈 Overall Test Statistics")
            
            try:
                test_stats = db.get_overall_test_statistics()
                
                if test_stats:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Tests", test_stats['total_tests'])
                    with col2:
                        st.metric("Total Scores Recorded", test_stats['total_scores'])
                    with col3:
                        st.metric("Average Score", f"{test_stats['overall_average']:.1f}%")
                    with col4:
                        st.metric("Tests This Month", test_stats['tests_this_month'])
                    
                    # Category-wise test statistics
                    category_stats = db.get_test_statistics_by_category()
                    
                    if not category_stats.empty:
                        fig = px.bar(
                            category_stats,
                            x='category',
                            y='average_score',
                            title="Average Performance by Category"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error loading statistics: {str(e)}")
            
            if st.button("Hide Statistics"):
                st.session_state['show_test_statistics'] = False
                st.rerun()
    else:
        st.info("No tests found. Create tests to start tracking performance.")

with tab5:
    st.subheader("📈 Progress Reports")
    
    # Report generation options
    report_type = st.selectbox(
        "Select Report Type",
        ["Individual Progress Report", "Batch Comparison Report", "Category Performance Report", "Trend Analysis Report"]
    )
    
    # Date range for reports
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Report Start Date", value=date.today() - timedelta(days=90))
    with col2:
        end_date = st.date_input("Report End Date", value=date.today())
    
    if report_type == "Individual Progress Report":
        students = db.get_all_students()
        
        if not students.empty:
            selected_students = st.multiselect(
                "Select Students for Report",
                students.apply(lambda x: f"{x['full_name']} - {x['batch']}", axis=1).tolist()
            )
            
            if selected_students and st.button("Generate Individual Reports"):
                for student_display in selected_students:
                    student_index = students.apply(lambda x: f"{x['full_name']} - {x['batch']}", axis=1).tolist().index(student_display)
                    student_data = students.iloc[student_index]
                    
                    st.subheader(f"📋 Progress Report: {student_data['full_name']}")
                    
                    # Generate individual report
                    report_data = db.generate_individual_progress_report(student_data['id'], start_date, end_date)
                    
                    if report_data:
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Tests Taken", report_data['tests_taken'])
                        with col2:
                            st.metric("Average Score", f"{report_data['average_score']:.1f}%")
                        with col3:
                            st.metric("Best Performance", f"{report_data['best_score']:.1f}%")
                        with col4:
                            st.metric("Attendance Rate", f"{report_data['attendance_rate']:.1f}%")
                        
                        # Performance trend
                        if 'performance_trend' in report_data and not report_data['performance_trend'].empty:
                            fig = px.line(
                                report_data['performance_trend'],
                                x='test_date',
                                y='percentage',
                                markers=True,
                                title=f"Performance Trend - {student_data['full_name']}"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommendations
                        st.write("**Recommendations:**")
                        for recommendation in report_data.get('recommendations', []):
                            st.write(f"• {recommendation}")
                    
                    st.divider()
    
    elif report_type == "Batch Comparison Report":
        batches = db.get_all_batches()
        
        if not batches.empty:
            selected_batches = st.multiselect(
                "Select Batches to Compare",
                batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist()
            )
            
            if selected_batches and st.button("Generate Batch Comparison"):
                comparison_data = []
                
                for batch_display in selected_batches:
                    batch_index = batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist().index(batch_display)
                    batch_data = batches.iloc[batch_index]
                    
                    batch_stats = db.get_batch_comparison_stats(batch_data['id'], start_date, end_date)
                    if batch_stats:
                        batch_stats['batch_name'] = batch_data['name']
                        comparison_data.append(batch_stats)
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    
                    # Comparison charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(
                            comparison_df,
                            x='batch_name',
                            y='average_score',
                            title="Average Performance Comparison"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.scatter(
                            comparison_df,
                            x='total_students',
                            y='average_score',
                            size='tests_conducted',
                            hover_name='batch_name',
                            title="Students vs Performance"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparison table
                    st.dataframe(
                        comparison_df[['batch_name', 'total_students', 'average_score', 'top_score', 'attendance_rate']],
                        use_container_width=True,
                        column_config={
                            "average_score": st.column_config.NumberColumn("Avg Score", format="%.1f%%"),
                            "top_score": st.column_config.NumberColumn("Top Score", format="%.1f%%"),
                            "attendance_rate": st.column_config.NumberColumn("Attendance", format="%.1f%%")
                        }
                    )
    
    elif report_type == "Category Performance Report":
        if st.button("Generate Category Report"):
            category_report = db.generate_category_performance_report(start_date, end_date)
            
            if not category_report.empty:
                # Category performance chart
                fig = px.bar(
                    category_report,
                    x='category',
                    y='average_performance',
                    color='student_count',
                    title="Performance by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed category table
                st.dataframe(
                    category_report,
                    use_container_width=True,
                    column_config={
                        "average_performance": st.column_config.NumberColumn("Avg Performance", format="%.1f%%")
                    }
                )
    
    elif report_type == "Trend Analysis Report":
        if st.button("Generate Trend Analysis"):
            trend_data = db.generate_trend_analysis_report(start_date, end_date)
            
            if trend_data:
                # Overall trends
                st.subheader("📈 Performance Trends")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'monthly_trends' in trend_data and not trend_data['monthly_trends'].empty:
                        fig = px.line(
                            trend_data['monthly_trends'],
                            x='month',
                            y='average_score',
                            title="Monthly Performance Trend"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'category_trends' in trend_data and not trend_data['category_trends'].empty:
                        fig = px.line(
                            trend_data['category_trends'],
                            x='month',
                            y='average_score',
                            color='category',
                            title="Category-wise Trends"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Key insights
                st.subheader("🎯 Key Insights")
                for insight in trend_data.get('insights', []):
                    st.write(f"• {insight}")
    
    # Export functionality for reports
    if st.button("📊 Export Current Report"):
        try:
            excel_data = db.export_progress_report(report_type, start_date, end_date)
            st.download_button(
                label=f"Download {report_type}",
                data=excel_data,
                file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
