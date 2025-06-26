import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import DatabaseManager
from utils.helpers import validate_phone_number, format_date

st.set_page_config(page_title="Student Management", page_icon="👨‍🎓", layout="wide")

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page first.")
    st.stop()

st.title("👨‍🎓 Student Management")

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📝 Add Student", "📋 View Students", "🔍 Search & Edit"])

with tab1:
    st.subheader("Add New Student")
    
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", placeholder="Enter student's full name")
            student_phone = st.text_input("Student's Phone Number", placeholder="Student's contact number")
            email = st.text_input("Email Address", placeholder="student@example.com")
        
        with col2:
            parent_phone = st.text_input("Parent's Phone Number *", placeholder="Parent's contact number")
            address = st.text_area("Address", placeholder="Complete address")
            date_of_birth = st.date_input("Date of Birth")
        
        # Category and Batch selection
        categories = db.get_categories()
        if not categories.empty:
            selected_category = st.selectbox("Select Category *", categories['name'].tolist())
            
            # Get batches for selected category
            if selected_category:
                batches = db.get_batches_by_category(selected_category)
                if not batches.empty:
                    selected_batch = st.selectbox("Select Batch *", batches['name'].tolist())
                else:
                    st.warning("No batches available for selected category. Please create a batch first.")
                    selected_batch = None
            else:
                selected_batch = None
        else:
            st.error("No categories available. Please create categories first.")
            selected_category = None
            selected_batch = None
        
        # Fee details
        st.subheader("Fee Information")
        col1, col2 = st.columns(2)
        with col1:
            total_fee = st.number_input("Total Fee Amount (₹)", min_value=0, value=0)
            paid_amount = st.number_input("Paid Amount (₹)", min_value=0, value=0)
        with col2:
            fee_due_date = st.date_input("Fee Due Date")
            discount = st.number_input("Discount (₹)", min_value=0, value=0)
        
        admission_date = st.date_input("Admission Date", value=datetime.now().date())
        notes = st.text_area("Additional Notes", placeholder="Any additional information about the student")
        
        submitted = st.form_submit_button("Add Student", type="primary")
        
        if submitted:
            # Validation
            errors = []
            if not full_name.strip():
                errors.append("Full name is required")
            if not parent_phone.strip():
                errors.append("Parent's phone number is required")
            if parent_phone and not validate_phone_number(parent_phone):
                errors.append("Invalid parent's phone number")
            if student_phone and not validate_phone_number(student_phone):
                errors.append("Invalid student's phone number")
            if not selected_category:
                errors.append("Category selection is required")
            if not selected_batch:
                errors.append("Batch selection is required")
            if paid_amount > total_fee:
                errors.append("Paid amount cannot exceed total fee")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    student_data = {
                        'full_name': full_name.strip(),
                        'parent_phone': parent_phone.strip(),
                        'student_phone': student_phone.strip() if student_phone else None,
                        'email': email.strip() if email else None,
                        'address': address.strip() if address else None,
                        'date_of_birth': date_of_birth,
                        'category': selected_category,
                        'batch': selected_batch,
                        'total_fee': total_fee,
                        'paid_amount': paid_amount,
                        'discount': discount,
                        'fee_due_date': fee_due_date,
                        'admission_date': admission_date,
                        'notes': notes.strip() if notes else None
                    }
                    
                    result = db.add_student(student_data)
                    if result:
                        st.success(f"✅ Student {full_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add student. Please try again.")
                except Exception as e:
                    st.error(f"Error adding student: {str(e)}")

with tab2:
    st.subheader("All Students")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        categories = db.get_categories()
        category_filter = st.selectbox("Filter by Category", ["All Categories"] + categories['name'].tolist() if not categories.empty else ["All Categories"])
    
    with col2:
        if category_filter != "All Categories":
            batches = db.get_batches_by_category(category_filter)
            batch_filter = st.selectbox("Filter by Batch", ["All Batches"] + batches['name'].tolist() if not batches.empty else ["All Batches"])
        else:
            batch_filter = st.selectbox("Filter by Batch", ["All Batches"])
    
    with col3:
        fee_status_filter = st.selectbox("Fee Status", ["All", "Paid", "Pending", "Overdue"])
    
    # Get filtered students
    try:
        students = db.get_students_filtered(category_filter, batch_filter, fee_status_filter)
        
        if not students.empty:
            st.dataframe(
                students,
                use_container_width=True,
                column_config={
                    "admission_date": st.column_config.DateColumn("Admission Date"),
                    "total_fee": st.column_config.NumberColumn("Total Fee", format="₹%.0f"),
                    "paid_amount": st.column_config.NumberColumn("Paid", format="₹%.0f"),
                    "pending_amount": st.column_config.NumberColumn("Pending", format="₹%.0f"),
                    "parent_phone": st.column_config.TextColumn("Parent's Phone"),
                    "student_phone": st.column_config.TextColumn("Student's Phone")
                }
            )
            
            # Export functionality
            if st.button("📊 Export to Excel"):
                excel_data = db.export_students_to_excel()
                st.download_button(
                    label="Download Excel File",
                    data=excel_data,
                    file_name=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No students found matching the selected filters.")
    
    except Exception as e:
        st.error(f"Error loading students: {str(e)}")

with tab3:
    st.subheader("Search & Edit Students")
    
    # Search functionality
    search_term = st.text_input("🔍 Search by name or phone number", placeholder="Enter student name or phone number")
    
    if search_term:
        try:
            search_results = db.search_students(search_term)
            
            if not search_results.empty:
                selected_student = st.selectbox(
                    "Select student to edit:",
                    search_results.apply(lambda x: f"{x['full_name']} - {x['parent_phone']} ({x['batch']})", axis=1).tolist()
                )
                
                if selected_student:
                    # Get selected student data
                    student_index = search_results.apply(lambda x: f"{x['full_name']} - {x['parent_phone']} ({x['batch']})", axis=1).tolist().index(selected_student)
                    student_data = search_results.iloc[student_index]
                    
                    # Edit form
                    with st.form("edit_student_form"):
                        st.write(f"**Editing:** {student_data['full_name']}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Full Name", value=student_data['full_name'])
                            edit_student_phone = st.text_input("Student's Phone", value=student_data.get('student_phone', ''))
                            edit_email = st.text_input("Email", value=student_data.get('email', ''))
                        
                        with col2:
                            edit_parent_phone = st.text_input("Parent's Phone", value=student_data['parent_phone'])
                            edit_address = st.text_area("Address", value=student_data.get('address', ''))
                        
                        # Fee information
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_total_fee = st.number_input("Total Fee", value=float(student_data['total_fee']))
                            edit_paid_amount = st.number_input("Paid Amount", value=float(student_data['paid_amount']))
                        with col2:
                            edit_discount = st.number_input("Discount", value=float(student_data.get('discount', 0)))
                        
                        edit_notes = st.text_area("Notes", value=student_data.get('notes', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            update_submitted = st.form_submit_button("Update Student", type="primary")
                        with col2:
                            delete_submitted = st.form_submit_button("Delete Student", type="secondary")
                        
                        if update_submitted:
                            try:
                                updated_data = {
                                    'id': student_data['id'],
                                    'full_name': edit_name,
                                    'parent_phone': edit_parent_phone,
                                    'student_phone': edit_student_phone,
                                    'email': edit_email,
                                    'address': edit_address,
                                    'total_fee': edit_total_fee,
                                    'paid_amount': edit_paid_amount,
                                    'discount': edit_discount,
                                    'notes': edit_notes
                                }
                                
                                if db.update_student(updated_data):
                                    st.success("✅ Student updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update student.")
                            except Exception as e:
                                st.error(f"Error updating student: {str(e)}")
                        
                        if delete_submitted:
                            if st.session_state.get('confirm_delete', False):
                                try:
                                    if db.delete_student(student_data['id']):
                                        st.success("✅ Student deleted successfully!")
                                        st.session_state.confirm_delete = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete student.")
                                except Exception as e:
                                    st.error(f"Error deleting student: {str(e)}")
                            else:
                                st.session_state.confirm_delete = True
                                st.warning("⚠️ Click Delete again to confirm permanent deletion.")
            else:
                st.info("No students found matching your search.")
        
        except Exception as e:
            st.error(f"Error searching students: {str(e)}")
