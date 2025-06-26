import streamlit as st
import pandas as pd
from utils.database import DatabaseManager
from utils.whatsapp import WhatsAppManager
from utils.helpers import format_phone_number
from datetime import datetime

st.set_page_config(page_title="Communication Center", page_icon="📱", layout="wide")

# Initialize database and WhatsApp manager
@st.cache_resource
def init_managers():
    db = DatabaseManager()
    wa = WhatsAppManager()
    return db, wa

db, wa = init_managers()

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page first.")
    st.stop()

st.title("📱 Communication Center")

# Tabs for different communication features
tab1, tab2, tab3, tab4 = st.tabs(["💬 Send Messages", "📝 Message Templates", "👥 Batch Communication", "📊 Message History"])

with tab1:
    st.subheader("Send WhatsApp Messages")
    
    # Message recipient selection
    recipient_type = st.radio("Select Recipients", ["Individual Students", "Entire Batch", "Custom Selection"])
    
    selected_recipients = []
    
    if recipient_type == "Individual Students":
        # Individual student selection
        students = db.get_all_students()
        if not students.empty:
            selected_students = st.multiselect(
                "Select Students",
                students.apply(lambda x: f"{x['full_name']} ({x['parent_phone']}) - {x['batch']}", axis=1).tolist(),
                help="Select one or more students to send messages to"
            )
            
            if selected_students:
                for student_str in selected_students:
                    student_index = students.apply(lambda x: f"{x['full_name']} ({x['parent_phone']}) - {x['batch']}", axis=1).tolist().index(student_str)
                    student = students.iloc[student_index]
                    selected_recipients.append({
                        'name': student['full_name'],
                        'phone': student['parent_phone'],
                        'type': 'individual'
                    })
        else:
            st.warning("No students found. Please add students first.")
    
    elif recipient_type == "Entire Batch":
        # Batch selection
        batches = db.get_all_batches()
        if not batches.empty:
            selected_batch = st.selectbox(
                "Select Batch",
                batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist()
            )
            
            if selected_batch:
                batch_index = batches.apply(lambda x: f"{x['name']} ({x['category']})", axis=1).tolist().index(selected_batch)
                batch_data = batches.iloc[batch_index]
                
                # Get students in batch
                batch_students = db.get_students_by_batch(batch_data['id'])
                
                if not batch_students.empty:
                    st.info(f"This will send messages to {len(batch_students)} students in the batch.")
                    
                    # Check if batch has WhatsApp group
                    if batch_data.get('whatsapp_group_link'):
                        st.success(f"✅ Batch has WhatsApp group: [Open Group Chat]({batch_data['whatsapp_group_link']})")
                    
                    for _, student in batch_students.iterrows():
                        selected_recipients.append({
                            'name': student['full_name'],
                            'phone': student['parent_phone'],
                            'type': 'batch',
                            'batch_name': batch_data['name']
                        })
                else:
                    st.warning(f"No students found in batch '{batch_data['name']}'.")
        else:
            st.warning("No batches found. Please create batches first.")
    
    elif recipient_type == "Custom Selection":
        # Custom selection interface
        categories = db.get_categories()
        if not categories.empty:
            filter_category = st.selectbox("Filter by Category (Optional)", ["All Categories"] + categories['name'].tolist())
            
            if filter_category != "All Categories":
                students = db.get_students_by_category(filter_category)
            else:
                students = db.get_all_students()
            
            if not students.empty:
                # Custom filters
                col1, col2 = st.columns(2)
                with col1:
                    fee_status_filter = st.selectbox("Fee Status Filter", ["All", "Pending Fees Only", "Paid Up"])
                
                with col2:
                    admission_period = st.selectbox("Admission Period", ["All Time", "This Month", "Last 3 Months", "This Year"])
                
                # Apply filters
                filtered_students = db.get_students_with_filters(filter_category, fee_status_filter, admission_period)
                
                if not filtered_students.empty:
                    st.write(f"**{len(filtered_students)} students match your criteria:**")
                    
                    # Select all checkbox
                    select_all = st.checkbox("Select All")
                    
                    selected_student_indices = []
                    for i, (_, student) in enumerate(filtered_students.iterrows()):
                        default_checked = select_all
                        if st.checkbox(
                            f"{student['full_name']} - {student['parent_phone']} ({student['batch']})",
                            value=default_checked,
                            key=f"student_{i}"
                        ):
                            selected_student_indices.append(i)
                    
                    # Add selected students to recipients
                    for i in selected_student_indices:
                        student = filtered_students.iloc[i]
                        selected_recipients.append({
                            'name': student['full_name'],
                            'phone': student['parent_phone'],
                            'type': 'custom'
                        })
    
    # Message composition
    if selected_recipients:
        st.subheader("Compose Message")
        
        # Load message templates
        templates = db.get_message_templates()
        template_names = ["Custom Message"] + templates['name'].tolist() if not templates.empty else ["Custom Message"]
        
        selected_template = st.selectbox("Use Template", template_names)
        
        if selected_template != "Custom Message" and not templates.empty:
            template_data = templates[templates['name'] == selected_template].iloc[0]
            message_text = st.text_area(
                "Message Text",
                value=template_data['content'],
                height=150,
                help="You can edit the template message before sending"
            )
        else:
            message_text = st.text_area(
                "Message Text",
                placeholder="Type your message here...",
                height=150
            )
        
        # Message personalization options
        st.write("**Message Personalization:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            include_name = st.checkbox("Include Student Name", value=True)
        with col2:
            include_batch = st.checkbox("Include Batch Information")
        with col3:
            include_fees = st.checkbox("Include Fee Information")
        
        # Preview message
        if st.button("👁️ Preview Message"):
            st.subheader("Message Preview")
            
            sample_recipient = selected_recipients[0]
            preview_message = wa.personalize_message(
                message_text,
                sample_recipient['name'],
                sample_recipient.get('batch_name', 'Sample Batch'),
                include_name,
                include_batch,
                include_fees
            )
            
            st.text_area("Preview (for first recipient):", value=preview_message, height=100, disabled=True)
        
        # Generate WhatsApp links
        if st.button("📱 Generate WhatsApp Links", type="primary"):
            if not message_text.strip():
                st.error("Please enter a message to send.")
            else:
                st.subheader("WhatsApp Message Links")
                st.info("Click on the links below to send messages via WhatsApp:")
                
                links_generated = 0
                for recipient in selected_recipients:
                    try:
                        # Personalize message for each recipient
                        personalized_message = wa.personalize_message(
                            message_text,
                            recipient['name'],
                            recipient.get('batch_name', ''),
                            include_name,
                            include_batch,
                            include_fees
                        )
                        
                        # Generate WhatsApp link
                        whatsapp_link = wa.generate_whatsapp_link(recipient['phone'], personalized_message)
                        
                        # Display link
                        st.markdown(f"**{recipient['name']}** ({format_phone_number(recipient['phone'])})")
                        st.link_button(f"📱 Send to {recipient['name']}", whatsapp_link)
                        
                        links_generated += 1
                        
                    except Exception as e:
                        st.error(f"Error generating link for {recipient['name']}: {str(e)}")
                
                if links_generated > 0:
                    # Log communication activity
                    try:
                        db.log_communication_activity({
                            'recipients': selected_recipients,
                            'message': message_text,
                            'template_used': selected_template if selected_template != "Custom Message" else None,
                            'timestamp': datetime.now()
                        })
                    except Exception as e:
                        st.warning(f"Message links generated but logging failed: {str(e)}")
                    
                    st.success(f"✅ Generated {links_generated} WhatsApp message links!")
    else:
        st.info("Please select recipients to compose and send messages.")

with tab2:
    st.subheader("📝 Message Templates")
    
    # Add new template
    with st.expander("➕ Create New Template"):
        with st.form("add_template_form"):
            template_name = st.text_input("Template Name *", placeholder="e.g., Fee Reminder, Exam Notice")
            template_category = st.selectbox("Category", ["General", "Fee Reminder", "Exam Notice", "Holiday Notice", "Admission"])
            template_content = st.text_area(
                "Template Content *",
                placeholder="Hello {student_name}, this is a reminder...",
                height=150,
                help="Use {student_name}, {batch_name}, {fee_amount} for personalization"
            )
            
            submitted = st.form_submit_button("Save Template")
            
            if submitted:
                if not template_name.strip() or not template_content.strip():
                    st.error("Template name and content are required.")
                else:
                    try:
                        template_data = {
                            'name': template_name.strip(),
                            'category': template_category,
                            'content': template_content.strip()
                        }
                        
                        if db.add_message_template(template_data):
                            st.success(f"✅ Template '{template_name}' saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save template.")
                    except Exception as e:
                        st.error(f"Error saving template: {str(e)}")
    
    # Display existing templates
    st.subheader("Saved Templates")
    
    try:
        templates = db.get_message_templates()
        
        if not templates.empty:
            # Category filter
            template_categories = ["All Categories"] + templates['category'].unique().tolist()
            category_filter = st.selectbox("Filter by Category", template_categories)
            
            if category_filter != "All Categories":
                filtered_templates = templates[templates['category'] == category_filter]
            else:
                filtered_templates = templates
            
            for _, template in filtered_templates.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{template['name']}** ({template['category']})")
                        st.text(template['content'][:100] + "..." if len(template['content']) > 100 else template['content'])
                    
                    with col2:
                        if st.button("✏️", key=f"edit_template_{template['id']}", help="Edit Template"):
                            st.session_state[f'edit_template_{template["id"]}'] = True
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_template_{template['id']}", help="Delete Template"):
                            if db.delete_message_template(template['id']):
                                st.success("Template deleted successfully!")
                                st.rerun()
                    
                    # Edit template form
                    if st.session_state.get(f'edit_template_{template["id"]}', False):
                        with st.form(f"edit_template_form_{template['id']}"):
                            new_name = st.text_input("Template Name", value=template['name'])
                            new_category = st.selectbox("Category", ["General", "Fee Reminder", "Exam Notice", "Holiday Notice", "Admission"], 
                                                      index=["General", "Fee Reminder", "Exam Notice", "Holiday Notice", "Admission"].index(template['category']))
                            new_content = st.text_area("Content", value=template['content'], height=150)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                update_template = st.form_submit_button("Update Template")
                            with col2:
                                cancel_template = st.form_submit_button("Cancel")
                            
                            if update_template:
                                try:
                                    if db.update_message_template(template['id'], {
                                        'name': new_name,
                                        'category': new_category,
                                        'content': new_content
                                    }):
                                        st.success("Template updated successfully!")
                                        st.session_state[f'edit_template_{template["id"]}'] = False
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating template: {str(e)}")
                            
                            if cancel_template:
                                st.session_state[f'edit_template_{template["id"]}'] = False
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No message templates found. Create your first template above.")
    
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")

with tab3:
    st.subheader("👥 Batch Communication")
    
    # Quick batch messaging
    batches = db.get_all_batches()
    
    if not batches.empty:
        for _, batch in batches.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 2])
                
                with col1:
                    st.markdown(f"**{batch['name']}** ({batch['category']})")
                    student_count = db.get_batch_student_count(batch['id'])
                    st.caption(f"👥 {student_count} students enrolled")
                
                with col2:
                    if batch.get('whatsapp_group_link'):
                        st.link_button("💬 Open Group", batch['whatsapp_group_link'])
                    else:
                        st.info("No group link")
                
                with col3:
                    if st.button("📱 Message Batch", key=f"msg_batch_{batch['id']}"):
                        st.session_state['selected_batch_for_msg'] = batch['id']
                        st.session_state['batch_msg_expanded'] = True
                
                # Batch messaging form
                if (st.session_state.get('selected_batch_for_msg') == batch['id'] and 
                    st.session_state.get('batch_msg_expanded', False)):
                    
                    with st.form(f"batch_message_form_{batch['id']}"):
                        st.write(f"**Send message to all students in {batch['name']}**")
                        
                        # Template selection
                        templates = db.get_message_templates()
                        template_options = ["Custom Message"] + templates['name'].tolist() if not templates.empty else ["Custom Message"]
                        selected_template = st.selectbox("Use Template", template_options, key=f"template_{batch['id']}")
                        
                        if selected_template != "Custom Message" and not templates.empty:
                            template_content = templates[templates['name'] == selected_template].iloc[0]['content']
                            batch_message = st.text_area("Message", value=template_content, height=120)
                        else:
                            batch_message = st.text_area("Message", height=120, placeholder="Enter your message...")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            send_batch_msg = st.form_submit_button("📱 Generate WhatsApp Links", type="primary")
                        with col2:
                            cancel_batch_msg = st.form_submit_button("Cancel")
                        
                        if send_batch_msg:
                            if batch_message.strip():
                                batch_students = db.get_students_by_batch(batch['id'])
                                
                                if not batch_students.empty:
                                    st.write("**WhatsApp Links for Batch Students:**")
                                    
                                    for _, student in batch_students.iterrows():
                                        personalized_msg = wa.personalize_message(
                                            batch_message,
                                            student['full_name'],
                                            batch['name'],
                                            True, True, False
                                        )
                                        
                                        whatsapp_link = wa.generate_whatsapp_link(student['parent_phone'], personalized_msg)
                                        st.link_button(
                                            f"📱 {student['full_name']} ({format_phone_number(student['parent_phone'])})",
                                            whatsapp_link
                                        )
                                    
                                    st.success(f"✅ Generated WhatsApp links for {len(batch_students)} students!")
                                else:
                                    st.warning("No students found in this batch.")
                            else:
                                st.error("Please enter a message.")
                        
                        if cancel_batch_msg:
                            st.session_state['batch_msg_expanded'] = False
                            st.rerun()
                
                st.divider()
    else:
        st.info("No batches found. Please create batches first.")

with tab4:
    st.subheader("📊 Message History")
    
    try:
        # Communication statistics
        comm_stats = db.get_communication_statistics()
        
        if comm_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Messages Today", comm_stats.get('today', 0))
            with col2:
                st.metric("This Week", comm_stats.get('this_week', 0))
            with col3:
                st.metric("This Month", comm_stats.get('this_month', 0))
            with col4:
                st.metric("Total Messages", comm_stats.get('total', 0))
        
        # Recent communication logs
        st.subheader("Recent Communications")
        
        comm_logs = db.get_communication_logs()
        
        if not comm_logs.empty:
            # Date filter
            date_filter = st.selectbox("Filter by Period", ["Last 7 Days", "Last 30 Days", "All Time"])
            
            filtered_logs = db.filter_communication_logs(comm_logs, date_filter)
            
            if not filtered_logs.empty:
                st.dataframe(
                    filtered_logs,
                    use_container_width=True,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn("Date & Time"),
                        "recipient_count": st.column_config.NumberColumn("Recipients"),
                        "template_used": st.column_config.TextColumn("Template")
                    }
                )
                
                # Export communication logs
                if st.button("📊 Export Communication History"):
                    excel_data = db.export_communication_logs_to_excel()
                    st.download_button(
                        label="Download Communication History",
                        data=excel_data,
                        file_name=f"communication_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No communication logs found for the selected period.")
        else:
            st.info("No communication history available yet.")
    
    except Exception as e:
        st.error(f"Error loading communication history: {str(e)}")
