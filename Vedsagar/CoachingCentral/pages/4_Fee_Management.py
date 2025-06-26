import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from utils.database import DatabaseManager
from utils.whatsapp import WhatsAppManager
from utils.helpers import format_currency, format_phone_number

st.set_page_config(page_title="Fee Management", page_icon="💰", layout="wide")

# Initialize managers
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

st.title("💰 Fee Management")

# Tabs for different fee management features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💳 Fee Overview", "📝 Record Payment", "⚠️ Pending Fees", "📱 Fee Reminders", "📊 Reports"])

with tab1:
    st.subheader("Fee Collection Overview")
    
    try:
        # Fee statistics
        fee_stats = db.get_fee_statistics()
        
        if fee_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Fees Expected",
                    format_currency(fee_stats.get('total_expected', 0)),
                    delta=f"{fee_stats.get('expected_growth', 0)}% vs last month"
                )
            
            with col2:
                st.metric(
                    "Collected This Month",
                    format_currency(fee_stats.get('collected_this_month', 0)),
                    delta=f"{fee_stats.get('collection_growth', 0)}% vs last month"
                )
            
            with col3:
                pending_amount = fee_stats.get('total_pending', 0)
                st.metric(
                    "Pending Amount",
                    format_currency(pending_amount),
                    delta=f"{fee_stats.get('pending_count', 0)} students"
                )
            
            with col4:
                collection_rate = fee_stats.get('collection_rate', 0)
                st.metric(
                    "Collection Rate",
                    f"{collection_rate:.1f}%",
                    delta="Target: 90%"
                )
        
        # Fee collection chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Monthly Collection Trend")
            monthly_data = db.get_monthly_fee_collection()
            
            if not monthly_data.empty:
                fig = px.line(
                    monthly_data,
                    x='month',
                    y='amount',
                    title="Fee Collection Over Time",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No collection data available yet.")
        
        with col2:
            st.subheader("🎯 Collection by Category")
            category_data = db.get_fee_collection_by_category()
            
            if not category_data.empty:
                fig = px.pie(
                    category_data,
                    values='collected_amount',
                    names='category',
                    title="Fee Collection by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category-wise data available.")
        
        # Recent payments
        st.subheader("Recent Payments")
        recent_payments = db.get_recent_payments()
        
        if not recent_payments.empty:
            st.dataframe(
                recent_payments.head(10),
                use_container_width=True,
                column_config={
                    "payment_date": st.column_config.DateColumn("Payment Date"),
                    "amount": st.column_config.NumberColumn("Amount", format="₹%.0f")
                }
            )
        else:
            st.info("No recent payments to display.")
    
    except Exception as e:
        st.error(f"Error loading fee overview: {str(e)}")

with tab2:
    st.subheader("📝 Record Payment")
    
    # Student selection for payment
    students = db.get_students_with_pending_fees()
    
    if not students.empty:
        # Search and select student
        search_student = st.text_input("🔍 Search Student", placeholder="Enter student name or phone number")
        
        if search_student:
            filtered_students = students[
                students['full_name'].str.contains(search_student, case=False, na=False) |
                students['parent_phone'].str.contains(search_student, na=False)
            ]
        else:
            filtered_students = students
        
        if not filtered_students.empty:
            selected_student_display = st.selectbox(
                "Select Student for Payment",
                filtered_students.apply(
                    lambda x: f"{x['full_name']} - {x['batch']} (Pending: {format_currency(x['pending_amount'])})",
                    axis=1
                ).tolist()
            )
            
            if selected_student_display:
                # Get selected student data
                student_index = filtered_students.apply(
                    lambda x: f"{x['full_name']} - {x['batch']} (Pending: {format_currency(x['pending_amount'])})",
                    axis=1
                ).tolist().index(selected_student_display)
                
                selected_student = filtered_students.iloc[student_index]
                
                # Payment form
                with st.form("payment_form"):
                    st.write(f"**Recording payment for:** {selected_student['full_name']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Total Fee:** {format_currency(selected_student['total_fee'])}")
                        st.info(f"**Already Paid:** {format_currency(selected_student['paid_amount'])}")
                        st.warning(f"**Pending Amount:** {format_currency(selected_student['pending_amount'])}")
                    
                    with col2:
                        payment_amount = st.number_input(
                            "Payment Amount (₹) *",
                            min_value=1,
                            max_value=float(selected_student['pending_amount']),
                            value=float(selected_student['pending_amount'])
                        )
                        
                        payment_method = st.selectbox(
                            "Payment Method",
                            ["Cash", "UPI", "Bank Transfer", "Cheque", "Card", "Online"]
                        )
                        
                        payment_date = st.date_input("Payment Date", value=datetime.now().date())
                    
                    transaction_reference = st.text_input(
                        "Transaction Reference/Receipt No.",
                        placeholder="Optional - Enter transaction ID or receipt number"
                    )
                    
                    payment_notes = st.text_area(
                        "Payment Notes",
                        placeholder="Any additional notes about this payment"
                    )
                    
                    # Fee adjustment options
                    with st.expander("⚙️ Fee Adjustments (Optional)"):
                        late_fee = st.number_input("Late Fee (₹)", min_value=0, value=0)
                        discount_applied = st.number_input("Additional Discount (₹)", min_value=0, value=0)
                        
                        if late_fee > 0:
                            st.warning(f"Late fee of {format_currency(late_fee)} will be added to total fee.")
                        if discount_applied > 0:
                            st.info(f"Discount of {format_currency(discount_applied)} will be applied.")
                    
                    submitted = st.form_submit_button("💰 Record Payment", type="primary")
                    
                    if submitted:
                        try:
                            payment_data = {
                                'student_id': selected_student['id'],
                                'amount': payment_amount,
                                'payment_method': payment_method,
                                'payment_date': payment_date,
                                'transaction_reference': transaction_reference,
                                'notes': payment_notes,
                                'late_fee': late_fee,
                                'discount': discount_applied
                            }
                            
                            result = db.record_payment(payment_data)
                            
                            if result:
                                st.success(f"✅ Payment of {format_currency(payment_amount)} recorded successfully!")
                                
                                # Generate payment receipt
                                receipt_data = db.generate_payment_receipt(result['payment_id'])
                                
                                if receipt_data:
                                    st.success("📧 Payment receipt generated!")
                                    
                                    # Option to send WhatsApp confirmation
                                    if st.button("📱 Send Payment Confirmation via WhatsApp"):
                                        confirmation_message = wa.generate_payment_confirmation_message(
                                            selected_student['full_name'],
                                            payment_amount,
                                            payment_date,
                                            selected_student['pending_amount'] - payment_amount
                                        )
                                        
                                        whatsapp_link = wa.generate_whatsapp_link(
                                            selected_student['parent_phone'],
                                            confirmation_message
                                        )
                                        
                                        st.link_button("📱 Send Payment Confirmation", whatsapp_link)
                                
                                st.rerun()
                            else:
                                st.error("Failed to record payment. Please try again.")
                        
                        except Exception as e:
                            st.error(f"Error recording payment: {str(e)}")
        else:
            st.info("No students found matching your search.")
    else:
        st.info("No students with pending fees found.")

with tab3:
    st.subheader("⚠️ Pending Fees Management")
    
    try:
        # Pending fees overview
        pending_fees = db.get_detailed_pending_fees()
        
        if not pending_fees.empty:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_pending = pending_fees['pending_amount'].sum()
                st.metric("Total Pending Amount", format_currency(total_pending))
            
            with col2:
                overdue_count = len(pending_fees[pending_fees['days_overdue'] > 0])
                st.metric("Overdue Students", overdue_count)
            
            with col3:
                avg_pending = pending_fees['pending_amount'].mean()
                st.metric("Average Pending", format_currency(avg_pending))
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fee_range = st.selectbox(
                    "Filter by Amount",
                    ["All Amounts", "< ₹10,000", "₹10,000 - ₹25,000", "> ₹25,000"]
                )
            
            with col2:
                overdue_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "Overdue Only", "Due Soon (7 days)", "Due This Month"]
                )
            
            with col3:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All Categories"] + pending_fees['category'].unique().tolist()
                )
            
            # Apply filters
            filtered_pending = db.apply_pending_fees_filters(pending_fees, fee_range, overdue_filter, category_filter)
            
            if not filtered_pending.empty:
                # Add priority indicators
                def get_priority_indicator(row):
                    if row['days_overdue'] > 30:
                        return "🔴 High Priority"
                    elif row['days_overdue'] > 0:
                        return "🟡 Overdue"
                    elif row['days_until_due'] <= 7:
                        return "🟠 Due Soon"
                    else:
                        return "🟢 Normal"
                
                filtered_pending['priority'] = filtered_pending.apply(get_priority_indicator, axis=1)
                
                # Display pending fees table
                st.dataframe(
                    filtered_pending[[
                        'full_name', 'batch', 'category', 'pending_amount', 
                        'fee_due_date', 'priority', 'parent_phone'
                    ]],
                    use_container_width=True,
                    column_config={
                        "pending_amount": st.column_config.NumberColumn("Pending Amount", format="₹%.0f"),
                        "fee_due_date": st.column_config.DateColumn("Due Date"),
                        "priority": st.column_config.TextColumn("Priority")
                    }
                )
                
                # Bulk actions
                st.subheader("📱 Bulk Actions")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📱 Send Reminders to Overdue"):
                        overdue_students = filtered_pending[filtered_pending['days_overdue'] > 0]
                        if not overdue_students.empty:
                            st.session_state['bulk_reminder_overdue'] = overdue_students
                            st.success(f"Prepared reminders for {len(overdue_students)} overdue students.")
                
                with col2:
                    if st.button("📱 Send Reminders to Due Soon"):
                        due_soon_students = filtered_pending[
                            (filtered_pending['days_overdue'] <= 0) & 
                            (filtered_pending['days_until_due'] <= 7)
                        ]
                        if not due_soon_students.empty:
                            st.session_state['bulk_reminder_due_soon'] = due_soon_students
                            st.success(f"Prepared reminders for {len(due_soon_students)} students due soon.")
                
                with col3:
                    if st.button("📊 Export Pending Fees"):
                        excel_data = db.export_pending_fees_to_excel(filtered_pending)
                        st.download_button(
                            label="Download Pending Fees Report",
                            data=excel_data,
                            file_name=f"pending_fees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                # Display bulk reminder links
                if 'bulk_reminder_overdue' in st.session_state:
                    st.subheader("📱 Overdue Fee Reminder Links")
                    
                    for _, student in st.session_state['bulk_reminder_overdue'].iterrows():
                        reminder_message = wa.generate_overdue_fee_reminder(
                            student['full_name'],
                            student['pending_amount'],
                            student['days_overdue']
                        )
                        
                        whatsapp_link = wa.generate_whatsapp_link(student['parent_phone'], reminder_message)
                        st.link_button(
                            f"📱 {student['full_name']} - {format_currency(student['pending_amount'])} (Overdue: {student['days_overdue']} days)",
                            whatsapp_link
                        )
                    
                    if st.button("Clear Overdue Reminders"):
                        del st.session_state['bulk_reminder_overdue']
                        st.rerun()
                
                if 'bulk_reminder_due_soon' in st.session_state:
                    st.subheader("📱 Due Soon Reminder Links")
                    
                    for _, student in st.session_state['bulk_reminder_due_soon'].iterrows():
                        reminder_message = wa.generate_due_soon_fee_reminder(
                            student['full_name'],
                            student['pending_amount'],
                            student['fee_due_date']
                        )
                        
                        whatsapp_link = wa.generate_whatsapp_link(student['parent_phone'], reminder_message)
                        st.link_button(
                            f"📱 {student['full_name']} - {format_currency(student['pending_amount'])} (Due: {student['fee_due_date']})",
                            whatsapp_link
                        )
                    
                    if st.button("Clear Due Soon Reminders"):
                        del st.session_state['bulk_reminder_due_soon']
                        st.rerun()
            else:
                st.info("No pending fees found matching the selected filters.")
        else:
            st.success("🎉 No pending fees! All students are up to date with their payments.")
    
    except Exception as e:
        st.error(f"Error loading pending fees: {str(e)}")

with tab4:
    st.subheader("📱 Fee Reminder Templates")
    
    # Create/manage fee reminder templates
    with st.expander("➕ Create Fee Reminder Template"):
        with st.form("fee_reminder_template_form"):
            template_name = st.text_input("Template Name", placeholder="e.g., Gentle Reminder, Final Notice")
            template_type = st.selectbox("Reminder Type", ["Due Soon", "Overdue", "Final Notice", "Custom"])
            
            default_messages = {
                "Due Soon": "Dear {student_name}, this is a gentle reminder that your fee of {pending_amount} for {batch} is due on {due_date}. Please make the payment at your earliest convenience. Thank you!",
                "Overdue": "Dear Parent, your ward {student_name}'s fee of {pending_amount} for {batch} is overdue by {days_overdue} days. Please make the payment immediately to avoid any inconvenience. Contact us for any queries.",
                "Final Notice": "FINAL NOTICE: Dear Parent, despite previous reminders, the fee of {pending_amount} for {student_name} ({batch}) remains unpaid. Please clear the dues immediately to continue classes. Contact: [Your Contact]",
                "Custom": ""
            }
            
            template_content = st.text_area(
                "Template Content",
                value=default_messages.get(template_type, ""),
                height=150,
                help="Available placeholders: {student_name}, {pending_amount}, {batch}, {due_date}, {days_overdue}"
            )
            
            if st.form_submit_button("Save Template"):
                try:
                    template_data = {
                        'name': template_name,
                        'type': template_type,
                        'content': template_content,
                        'category': 'fee_reminder'
                    }
                    
                    if db.add_message_template(template_data):
                        st.success("Fee reminder template saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save template.")
                except Exception as e:
                    st.error(f"Error saving template: {str(e)}")
    
    # Display existing fee reminder templates
    st.subheader("Existing Fee Reminder Templates")
    
    try:
        fee_templates = db.get_fee_reminder_templates()
        
        if not fee_templates.empty:
            for _, template in fee_templates.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{template['name']}** ({template['type']})")
                        st.text(template['content'][:100] + "..." if len(template['content']) > 100 else template['content'])
                    
                    with col2:
                        if st.button("📱 Use Template", key=f"use_template_{template['id']}"):
                            st.session_state['selected_fee_template'] = template
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_fee_template_{template['id']}", help="Delete Template"):
                            if db.delete_message_template(template['id']):
                                st.success("Template deleted!")
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No fee reminder templates found.")
    
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
    
    # Quick fee reminder sender
    if 'selected_fee_template' in st.session_state:
        template = st.session_state['selected_fee_template']
        
        st.subheader(f"📱 Send Reminders Using: {template['name']}")
        
        # Student selection for template
        pending_students = db.get_students_with_pending_fees()
        
        if not pending_students.empty:
            recipient_filter = st.selectbox(
                "Select Recipients",
                ["All Pending", "Overdue Only", "Due This Week", "Custom Selection"]
            )
            
            if recipient_filter == "Custom Selection":
                selected_students = st.multiselect(
                    "Choose Students",
                    pending_students.apply(
                        lambda x: f"{x['full_name']} - {format_currency(x['pending_amount'])}",
                        axis=1
                    ).tolist()
                )
                
                if selected_students:
                    target_students = pending_students[
                        pending_students.apply(
                            lambda x: f"{x['full_name']} - {format_currency(x['pending_amount'])}",
                            axis=1
                        ).isin(selected_students)
                    ]
                else:
                    target_students = pd.DataFrame()
            else:
                target_students = db.filter_students_for_reminders(pending_students, recipient_filter)
            
            if not target_students.empty:
                st.info(f"Will send reminders to {len(target_students)} students")
                
                if st.button("📱 Generate Reminder Links", type="primary"):
                    st.subheader("WhatsApp Reminder Links")
                    
                    for _, student in target_students.iterrows():
                        reminder_message = wa.personalize_fee_reminder(
                            template['content'],
                            student['full_name'],
                            student['pending_amount'],
                            student['batch'],
                            student.get('fee_due_date'),
                            student.get('days_overdue', 0)
                        )
                        
                        whatsapp_link = wa.generate_whatsapp_link(student['parent_phone'], reminder_message)
                        
                        st.link_button(
                            f"📱 {student['full_name']} - {format_currency(student['pending_amount'])}",
                            whatsapp_link
                        )
            else:
                st.info("No students match the selected criteria.")

with tab5:
    st.subheader("📊 Fee Management Reports")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Monthly Collection Summary", "Category-wise Analysis", "Payment Method Analysis", "Defaulter Report", "Fee Trends"]
    )
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To Date", value=date.today())
    
    try:
        if report_type == "Monthly Collection Summary":
            report_data = db.get_monthly_collection_report(start_date, end_date)
            
            if not report_data.empty:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Collected", format_currency(report_data['amount'].sum()))
                with col2:
                    st.metric("Average Monthly", format_currency(report_data['amount'].mean()))
                with col3:
                    st.metric("Transactions", report_data['transaction_count'].sum())
                
                # Chart
                fig = px.bar(report_data, x='month', y='amount', title="Monthly Fee Collection")
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(report_data, use_container_width=True)
        
        elif report_type == "Category-wise Analysis":
            report_data = db.get_category_wise_fee_report(start_date, end_date)
            
            if not report_data.empty:
                # Pie chart
                fig = px.pie(
                    report_data, 
                    values='collected_amount', 
                    names='category',
                    title="Fee Collection by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(report_data, use_container_width=True)
        
        elif report_type == "Payment Method Analysis":
            report_data = db.get_payment_method_report(start_date, end_date)
            
            if not report_data.empty:
                fig = px.bar(
                    report_data, 
                    x='payment_method', 
                    y='amount',
                    title="Collection by Payment Method"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(report_data, use_container_width=True)
        
        elif report_type == "Defaulter Report":
            report_data = db.get_defaulter_report()
            
            if not report_data.empty:
                # Highlight high-risk defaulters
                high_risk = report_data[report_data['days_overdue'] > 30]
                
                if not high_risk.empty:
                    st.error(f"⚠️ {len(high_risk)} high-risk defaulters (>30 days overdue)")
                    st.dataframe(
                        high_risk,
                        use_container_width=True,
                        column_config={
                            "pending_amount": st.column_config.NumberColumn("Pending", format="₹%.0f"),
                            "days_overdue": st.column_config.NumberColumn("Days Overdue")
                        }
                    )
                
                st.subheader("All Defaulters")
                st.dataframe(report_data, use_container_width=True)
        
        elif report_type == "Fee Trends":
            report_data = db.get_fee_trends_report(start_date, end_date)
            
            if not report_data.empty:
                # Multiple metrics chart
                fig = px.line(
                    report_data, 
                    x='date', 
                    y=['daily_collection', 'cumulative_collection'],
                    title="Fee Collection Trends"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(report_data, use_container_width=True)
        
        # Export functionality
        if 'report_data' in locals() and not report_data.empty:
            if st.button("📊 Export Report"):
                excel_data = db.export_report_to_excel(report_data, report_type)
                st.download_button(
                    label=f"Download {report_type} Report",
                    data=excel_data,
                    file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
