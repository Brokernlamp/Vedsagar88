import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.database import DatabaseManager
from utils.helpers import format_date

st.set_page_config(page_title="Batch Management", page_icon="📚", layout="wide")

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page first.")
    st.stop()

st.title("📚 Batch & Category Management")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📂 Categories", "📚 Batches", "📊 Batch Analytics", "⚙️ Settings"])

with tab1:
    st.subheader("Category Management")
    
    # Add new category
    with st.expander("➕ Add New Category"):
        with st.form("add_category_form"):
            cat_name = st.text_input("Category Name *", placeholder="e.g., NEET, JEE, UPSC")
            cat_description = st.text_area("Description", placeholder="Brief description of the category")
            cat_color = st.color_picker("Category Color", value="#1f77b4")
            
            submitted = st.form_submit_button("Add Category")
            
            if submitted:
                if not cat_name.strip():
                    st.error("Category name is required")
                else:
                    try:
                        category_data = {
                            'name': cat_name.strip(),
                            'description': cat_description.strip(),
                            'color': cat_color
                        }
                        
                        if db.add_category(category_data):
                            st.success(f"✅ Category '{cat_name}' added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add category. Category might already exist.")
                    except Exception as e:
                        st.error(f"Error adding category: {str(e)}")
    
    # Display existing categories
    st.subheader("Existing Categories")
    try:
        categories = db.get_categories_with_stats()
        
        if not categories.empty:
            for _, category in categories.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{category['name']}**")
                        st.caption(category.get('description', 'No description'))
                    
                    with col2:
                        st.metric("Students", category.get('student_count', 0))
                    
                    with col3:
                        st.metric("Batches", category.get('batch_count', 0))
                    
                    with col4:
                        if st.button("✏️", key=f"edit_cat_{category['id']}", help="Edit Category"):
                            st.session_state[f'edit_category_{category["id"]}'] = True
                    
                    with col5:
                        if st.button("🗑️", key=f"del_cat_{category['id']}", help="Delete Category"):
                            if category.get('student_count', 0) > 0:
                                st.error("Cannot delete category with students")
                            else:
                                if db.delete_category(category['id']):
                                    st.success("Category deleted successfully!")
                                    st.rerun()
                    
                    # Edit category form
                    if st.session_state.get(f'edit_category_{category["id"]}', False):
                        with st.form(f"edit_category_form_{category['id']}"):
                            new_name = st.text_input("Category Name", value=category['name'])
                            new_description = st.text_area("Description", value=category.get('description', ''))
                            new_color = st.color_picker("Color", value=category.get('color', '#1f77b4'))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                update_cat = st.form_submit_button("Update")
                            with col2:
                                cancel_cat = st.form_submit_button("Cancel")
                            
                            if update_cat:
                                try:
                                    if db.update_category(category['id'], {
                                        'name': new_name,
                                        'description': new_description,
                                        'color': new_color
                                    }):
                                        st.success("Category updated successfully!")
                                        st.session_state[f'edit_category_{category["id"]}'] = False
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating category: {str(e)}")
                            
                            if cancel_cat:
                                st.session_state[f'edit_category_{category["id"]}'] = False
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No categories found. Add a category to get started.")
    
    except Exception as e:
        st.error(f"Error loading categories: {str(e)}")

with tab2:
    st.subheader("Batch Management")
    
    # Add new batch
    with st.expander("➕ Add New Batch"):
        with st.form("add_batch_form"):
            categories = db.get_categories()
            
            if not categories.empty:
                batch_category = st.selectbox("Select Category *", categories['name'].tolist())
                batch_name = st.text_input("Batch Name *", placeholder="e.g., NEET Morning Batch")
                
                col1, col2 = st.columns(2)
                with col1:
                    batch_start_date = st.date_input("Start Date *")
                    batch_capacity = st.number_input("Maximum Capacity", min_value=1, value=30)
                    batch_fee = st.number_input("Batch Fee (₹)", min_value=0, value=0)
                
                with col2:
                    batch_end_date = st.date_input("End Date")
                    batch_schedule = st.text_input("Schedule", placeholder="e.g., Mon-Fri 9AM-12PM")
                    instructor_name = st.text_input("Instructor Name", placeholder="Primary instructor")
                
                batch_description = st.text_area("Description", placeholder="Batch details and syllabus")
                whatsapp_group_link = st.text_input("WhatsApp Group Link", placeholder="https://chat.whatsapp.com/...")
                
                submitted = st.form_submit_button("Create Batch")
                
                if submitted:
                    errors = []
                    if not batch_name.strip():
                        errors.append("Batch name is required")
                    if batch_end_date and batch_end_date <= batch_start_date:
                        errors.append("End date must be after start date")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        try:
                            batch_data = {
                                'name': batch_name.strip(),
                                'category': batch_category,
                                'start_date': batch_start_date,
                                'end_date': batch_end_date,
                                'capacity': batch_capacity,
                                'fee': batch_fee,
                                'schedule': batch_schedule.strip(),
                                'instructor': instructor_name.strip(),
                                'description': batch_description.strip(),
                                'whatsapp_group_link': whatsapp_group_link.strip() if whatsapp_group_link else None
                            }
                            
                            if db.add_batch(batch_data):
                                st.success(f"✅ Batch '{batch_name}' created successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to create batch.")
                        except Exception as e:
                            st.error(f"Error creating batch: {str(e)}")
            else:
                st.warning("Please create at least one category before adding batches.")
    
    # Display existing batches
    st.subheader("Existing Batches")
    
    # Category filter
    categories = db.get_categories()
    if not categories.empty:
        category_filter = st.selectbox("Filter by Category", ["All Categories"] + categories['name'].tolist())
        
        try:
            if category_filter == "All Categories":
                batches = db.get_all_batches()
            else:
                batches = db.get_batches_by_category(category_filter)
            
            if not batches.empty:
                for _, batch in batches.iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"**{batch['name']}** ({batch['category']})")
                            st.caption(f"📅 {format_date(batch['start_date'])} - {format_date(batch['end_date'])}")
                            if batch.get('schedule'):
                                st.caption(f"🕐 {batch['schedule']}")
                            if batch.get('instructor'):
                                st.caption(f"👨‍🏫 {batch['instructor']}")
                        
                        with col2:
                            current_students = batch.get('current_students', 0)
                            capacity = batch.get('capacity', 0)
                            st.metric("Enrollment", f"{current_students}/{capacity}")
                            
                            # Progress bar for capacity
                            if capacity > 0:
                                progress = min(current_students / capacity, 1.0)
                                st.progress(progress)
                        
                        with col3:
                            if batch.get('whatsapp_group_link'):
                                st.link_button("💬 WhatsApp Group", batch['whatsapp_group_link'])
                            
                            batch_status = "Active" if batch['start_date'] <= date.today() <= batch.get('end_date', date.today()) else "Upcoming"
                            if batch_status == "Active":
                                st.success("🟢 Active")
                            else:
                                st.info("🔵 Upcoming")
                        
                        with col4:
                            if st.button("👥", key=f"students_{batch['id']}", help="View Students"):
                                st.session_state[f'show_students_{batch["id"]}'] = True
                            
                            if st.button("✏️", key=f"edit_{batch['id']}", help="Edit Batch"):
                                st.session_state[f'edit_batch_{batch["id"]}'] = True
                        
                        # Show students in batch
                        if st.session_state.get(f'show_students_{batch["id"]}', False):
                            batch_students = db.get_students_by_batch(batch['id'])
                            if not batch_students.empty:
                                st.dataframe(
                                    batch_students[['full_name', 'parent_phone', 'admission_date']],
                                    use_container_width=True
                                )
                            else:
                                st.info("No students enrolled in this batch yet.")
                            
                            if st.button("Hide Students", key=f"hide_students_{batch['id']}"):
                                st.session_state[f'show_students_{batch["id"]}'] = False
                                st.rerun()
                        
                        # Edit batch form
                        if st.session_state.get(f'edit_batch_{batch["id"]}', False):
                            with st.form(f"edit_batch_form_{batch['id']}"):
                                st.write(f"**Editing Batch:** {batch['name']}")
                                
                                new_batch_name = st.text_input("Batch Name", value=batch['name'])
                                new_schedule = st.text_input("Schedule", value=batch.get('schedule', ''))
                                new_instructor = st.text_input("Instructor", value=batch.get('instructor', ''))
                                new_capacity = st.number_input("Capacity", value=batch.get('capacity', 30))
                                new_whatsapp_link = st.text_input("WhatsApp Group Link", value=batch.get('whatsapp_group_link', ''))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    update_batch = st.form_submit_button("Update Batch")
                                with col2:
                                    cancel_batch = st.form_submit_button("Cancel")
                                
                                if update_batch:
                                    try:
                                        updated_batch_data = {
                                            'name': new_batch_name,
                                            'schedule': new_schedule,
                                            'instructor': new_instructor,
                                            'capacity': new_capacity,
                                            'whatsapp_group_link': new_whatsapp_link
                                        }
                                        
                                        if db.update_batch(batch['id'], updated_batch_data):
                                            st.success("Batch updated successfully!")
                                            st.session_state[f'edit_batch_{batch["id"]}'] = False
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating batch: {str(e)}")
                                
                                if cancel_batch:
                                    st.session_state[f'edit_batch_{batch["id"]}'] = False
                                    st.rerun()
                        
                        st.divider()
            else:
                st.info("No batches found for the selected category.")
        
        except Exception as e:
            st.error(f"Error loading batches: {str(e)}")

with tab3:
    st.subheader("📊 Batch Analytics")
    
    try:
        # Batch capacity analysis
        batch_stats = db.get_batch_capacity_stats()
        
        if not batch_stats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Batches", len(batch_stats))
                st.metric("Average Capacity", f"{batch_stats['capacity'].mean():.0f}")
            
            with col2:
                st.metric("Total Enrolled", batch_stats['current_students'].sum())
                st.metric("Available Seats", (batch_stats['capacity'] - batch_stats['current_students']).sum())
            
            # Capacity utilization chart
            import plotly.express as px
            
            batch_stats['utilization'] = (batch_stats['current_students'] / batch_stats['capacity'] * 100).round(1)
            
            fig = px.bar(
                batch_stats,
                x='name',
                y='utilization',
                title="Batch Capacity Utilization (%)",
                labels={'utilization': 'Utilization %', 'name': 'Batch Name'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed stats table
            st.subheader("Detailed Batch Statistics")
            st.dataframe(
                batch_stats[['name', 'category', 'current_students', 'capacity', 'utilization']],
                use_container_width=True,
                column_config={
                    "utilization": st.column_config.NumberColumn("Utilization %", format="%.1f%%")
                }
            )
        else:
            st.info("No batch data available for analytics.")
    
    except Exception as e:
        st.error(f"Error loading batch analytics: {str(e)}")

with tab4:
    st.subheader("⚙️ Batch Settings")
    
    # Bulk operations
    st.write("**Bulk Operations**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export All Batches"):
            try:
                excel_data = db.export_batches_to_excel()
                st.download_button(
                    label="Download Batches Export",
                    data=excel_data,
                    file_name=f"batches_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error exporting batches: {str(e)}")
    
    with col2:
        if st.button("🗑️ Archive Old Batches"):
            try:
                archived_count = db.archive_completed_batches()
                st.success(f"Archived {archived_count} completed batches.")
            except Exception as e:
                st.error(f"Error archiving batches: {str(e)}")
    
    # System maintenance
    st.write("**System Maintenance**")
    
    if st.button("🔄 Refresh Batch Statistics"):
        try:
            db.refresh_batch_statistics()
            st.success("Batch statistics refreshed successfully!")
        except Exception as e:
            st.error(f"Error refreshing statistics: {str(e)}")
