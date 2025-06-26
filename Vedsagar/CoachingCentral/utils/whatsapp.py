import urllib.parse
from typing import List, Dict, Optional
from datetime import datetime, date

class WhatsAppManager:
    """
    WhatsApp message manager for the EduCRM system
    Handles WhatsApp link generation and message templating
    """
    
    def __init__(self):
        self.base_url = "https://wa.me/"
        self.web_url = "https://web.whatsapp.com/send"
    
    def clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number for WhatsApp"""
        if not phone:
            return ""
        
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present (assuming India +91)
        if len(cleaned) == 10:
            cleaned = "91" + cleaned
        elif len(cleaned) == 11 and cleaned.startswith("0"):
            cleaned = "91" + cleaned[1:]
        elif len(cleaned) == 13 and cleaned.startswith("91"):
            cleaned = cleaned  # Already has country code
        
        return cleaned
    
    def generate_whatsapp_link(self, phone: str, message: str, use_web: bool = False) -> str:
        """Generate WhatsApp message link"""
        try:
            cleaned_phone = self.clean_phone_number(phone)
            if not cleaned_phone:
                return ""
            
            # URL encode the message
            encoded_message = urllib.parse.quote(message)
            
            if use_web:
                # Web WhatsApp link
                return f"{self.web_url}?phone={cleaned_phone}&text={encoded_message}"
            else:
                # Mobile WhatsApp link
                return f"{self.base_url}{cleaned_phone}?text={encoded_message}"
        
        except Exception as e:
            print(f"Error generating WhatsApp link: {str(e)}")
            return ""
    
    def personalize_message(self, template: str, student_name: str, batch_name: str = "", 
                          include_name: bool = True, include_batch: bool = False, 
                          include_fees: bool = False, fee_amount: float = 0) -> str:
        """Personalize message template with student details"""
        try:
            message = template
            
            # Replace placeholders
            if include_name and student_name:
                message = message.replace("{student_name}", student_name)
                if not "{student_name}" in template and include_name:
                    message = f"Dear {student_name},\n\n{message}"
            
            if include_batch and batch_name:
                message = message.replace("{batch_name}", batch_name)
            
            if include_fees and fee_amount > 0:
                message = message.replace("{fee_amount}", f"₹{fee_amount:,.0f}")
                message = message.replace("{pending_amount}", f"₹{fee_amount:,.0f}")
            
            # Replace common placeholders
            message = message.replace("{institute_name}", "Our Coaching Institute")
            message = message.replace("{contact_number}", "Contact us for more details")
            
            return message.strip()
        
        except Exception as e:
            print(f"Error personalizing message: {str(e)}")
            return template
    
    def generate_fee_reminder_message(self, student_name: str, pending_amount: float, 
                                    due_date: str = "", batch_name: str = "", 
                                    reminder_type: str = "gentle") -> str:
        """Generate fee reminder message"""
        try:
            if reminder_type == "gentle":
                template = """Dear {student_name},

This is a gentle reminder that your fee payment of ₹{pending_amount} for {batch_name} is pending.

Please make the payment at your earliest convenience to avoid any interruption in your classes.

Due Date: {due_date}

Thank you for your cooperation!

Best regards,
EduCRM Team"""
            
            elif reminder_type == "urgent":
                template = """Dear Parent,

URGENT REMINDER: The fee payment of ₹{pending_amount} for your ward {student_name} ({batch_name}) is overdue.

Please clear the dues immediately to ensure uninterrupted classes.

Original Due Date: {due_date}

For any queries, please contact us immediately.

EduCRM Team"""
            
            elif reminder_type == "final":
                template = """FINAL NOTICE

Dear Parent,

Despite previous reminders, the fee of ₹{pending_amount} for {student_name} ({batch_name}) remains unpaid.

Please clear the outstanding amount within 24 hours to avoid suspension of classes.

Due Date: {due_date}

Contact our office immediately to resolve this matter.

EduCRM Administration"""
            
            else:
                template = """Dear {student_name},

Your fee payment of ₹{pending_amount} for {batch_name} is pending.

Please make the payment by {due_date}.

Thank you!"""
            
            # Personalize the message
            message = template.replace("{student_name}", student_name)
            message = message.replace("{pending_amount}", f"{pending_amount:,.0f}")
            message = message.replace("{batch_name}", batch_name)
            message = message.replace("{due_date}", due_date)
            
            return message
        
        except Exception as e:
            print(f"Error generating fee reminder: {str(e)}")
            return f"Fee reminder for {student_name}: ₹{pending_amount:,.0f} pending"
    
    def generate_overdue_fee_reminder(self, student_name: str, pending_amount: float, 
                                    days_overdue: int) -> str:
        """Generate overdue fee reminder message"""
        template = f"""🔴 OVERDUE NOTICE

Dear Parent,

Your ward {student_name}'s fee payment of ₹{pending_amount:,.0f} is overdue by {days_overdue} days.

Immediate payment is required to avoid any disruption in classes.

Please contact our office or make the payment today.

Thank you for your prompt attention.

EduCRM Team"""
        
        return template
    
    def generate_due_soon_fee_reminder(self, student_name: str, pending_amount: float, 
                                     due_date: date) -> str:
        """Generate due soon fee reminder message"""
        due_date_str = due_date.strftime("%d-%m-%Y") if isinstance(due_date, date) else str(due_date)
        
        template = f"""📅 PAYMENT DUE SOON

Dear Parent,

This is a friendly reminder that {student_name}'s fee payment of ₹{pending_amount:,.0f} is due on {due_date_str}.

Please make the payment by the due date to avoid any late fees.

Thank you for your cooperation!

EduCRM Team"""
        
        return template
    
    def generate_payment_confirmation_message(self, student_name: str, amount_paid: float, 
                                            payment_date: date, remaining_balance: float = 0) -> str:
        """Generate payment confirmation message"""
        payment_date_str = payment_date.strftime("%d-%m-%Y") if isinstance(payment_date, date) else str(payment_date)
        
        template = f"""✅ PAYMENT CONFIRMATION

Dear Parent,

We acknowledge the receipt of ₹{amount_paid:,.0f} for {student_name}'s fee payment on {payment_date_str}.

"""
        
        if remaining_balance > 0:
            template += f"Remaining balance: ₹{remaining_balance:,.0f}\n\n"
        else:
            template += "Your fee payment is now up to date.\n\n"
        
        template += """Thank you for your prompt payment!

Best regards,
EduCRM Team"""
        
        return template
    
    def generate_exam_notice_message(self, student_name: str, exam_name: str, 
                                   exam_date: str, batch_name: str = "") -> str:
        """Generate exam notice message"""
        template = f"""📝 EXAM NOTICE

Dear {student_name},

This is to inform you about the upcoming {exam_name}."""
        
        if batch_name:
            template += f"\n\nBatch: {batch_name}"
        
        template += f"""
Exam Date: {exam_date}

Please prepare well and be present on time.

Best of luck!

EduCRM Team"""
        
        return template
    
    def generate_holiday_notice_message(self, holiday_name: str, start_date: str, 
                                      end_date: str = "", batch_name: str = "") -> str:
        """Generate holiday notice message"""
        template = f"""🏖️ HOLIDAY NOTICE

Dear Students,

Our institute will be closed for {holiday_name}."""
        
        if end_date and end_date != start_date:
            template += f"\n\nFrom: {start_date}\nTo: {end_date}"
        else:
            template += f"\n\nDate: {start_date}"
        
        if batch_name:
            template += f"\n\nThis applies to: {batch_name}"
        
        template += """\n\nClasses will resume as per regular schedule after the holiday.

Stay safe and enjoy the break!

EduCRM Team"""
        
        return template
    
    def generate_admission_welcome_message(self, student_name: str, batch_name: str, 
                                         start_date: str, contact_number: str = "") -> str:
        """Generate welcome message for new admissions"""
        template = f"""🎉 WELCOME TO EduCRM

Dear {student_name},

Congratulations! Your admission to {batch_name} has been confirmed.

Classes start from: {start_date}

We are excited to have you as part of our learning community. Our experienced faculty and comprehensive study material will help you achieve your goals.

"""
        
        if contact_number:
            template += f"For any queries, contact us at: {contact_number}\n\n"
        
        template += """Best wishes for your academic journey!

EduCRM Team"""
        
        return template
    
    def generate_batch_announcement_message(self, announcement: str, batch_name: str, 
                                          date: str = "") -> str:
        """Generate batch announcement message"""
        template = f"""📢 BATCH ANNOUNCEMENT - {batch_name}

{announcement}

"""
        
        if date:
            template += f"Date: {date}\n\n"
        
        template += """For any clarifications, please contact the institute.

EduCRM Team"""
        
        return template
    
    def personalize_fee_reminder(self, template: str, student_name: str, pending_amount: float, 
                               batch_name: str, due_date: Optional[date], days_overdue: int = 0) -> str:
        """Personalize fee reminder template"""
        try:
            message = template
            
            # Replace placeholders
            message = message.replace("{student_name}", student_name)
            message = message.replace("{pending_amount}", f"₹{pending_amount:,.0f}")
            message = message.replace("{batch_name}", batch_name)
            
            if due_date:
                due_date_str = due_date.strftime("%d-%m-%Y") if isinstance(due_date, date) else str(due_date)
                message = message.replace("{due_date}", due_date_str)
            
            message = message.replace("{days_overdue}", str(days_overdue))
            
            return message
        
        except Exception as e:
            print(f"Error personalizing fee reminder: {str(e)}")
            return template
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        try:
            cleaned = self.clean_phone_number(phone)
            return len(cleaned) >= 12 and cleaned.isdigit()
        except Exception:
            return False
    
    def format_phone_display(self, phone: str) -> str:
        """Format phone number for display"""
        try:
            cleaned = self.clean_phone_number(phone)
            if len(cleaned) >= 12:
                # Format as +91 XXXXX XXXXX
                return f"+{cleaned[:2]} {cleaned[2:7]} {cleaned[7:]}"
            return phone
        except Exception:
            return phone
    
    def generate_bulk_message_data(self, recipients: List[Dict], message_template: str, 
                                 personalize: bool = True) -> List[Dict]:
        """Generate bulk message data for multiple recipients"""
        try:
            message_data = []
            
            for recipient in recipients:
                if personalize:
                    personalized_message = self.personalize_message(
                        message_template,
                        recipient.get('name', ''),
                        recipient.get('batch_name', ''),
                        include_name=True,
                        include_batch=True
                    )
                else:
                    personalized_message = message_template
                
                whatsapp_link = self.generate_whatsapp_link(
                    recipient.get('phone', ''),
                    personalized_message
                )
                
                message_data.append({
                    'name': recipient.get('name', ''),
                    'phone': recipient.get('phone', ''),
                    'message': personalized_message,
                    'whatsapp_link': whatsapp_link,
                    'valid_phone': self.validate_phone_number(recipient.get('phone', ''))
                })
            
            return message_data
        
        except Exception as e:
            print(f"Error generating bulk message data: {str(e)}")
            return []
