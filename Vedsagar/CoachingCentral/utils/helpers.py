import re
from datetime import datetime, date
from typing import Any, Optional, Union
import pandas as pd

def format_currency(amount: Union[int, float]) -> str:
    """Format currency amount in Indian Rupees"""
    try:
        if pd.isna(amount) or amount == 0:
            return "₹0"
        
        # Convert to float if string
        if isinstance(amount, str):
            amount = float(amount.replace(',', '').replace('₹', ''))
        
        # Format with commas for Indian numbering system
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.1f}Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.1f}L"
        elif amount >= 1000:  # thousands
            return f"₹{amount:,.0f}"
        else:
            return f"₹{amount:.0f}"
    
    except (ValueError, TypeError):
        return "₹0"

def format_phone_number(phone: str) -> str:
    """Format phone number for display"""
    try:
        if not phone:
            return ""
        
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Format based on length
        if len(cleaned) == 10:
            return f"{cleaned[:5]} {cleaned[5:]}"
        elif len(cleaned) == 11 and cleaned.startswith("0"):
            return f"{cleaned[:6]} {cleaned[6:]}"
        elif len(cleaned) >= 12:  # With country code
            if cleaned.startswith("91"):
                return f"+91 {cleaned[2:7]} {cleaned[7:]}"
            else:
                return f"+{cleaned[:2]} {cleaned[2:7]} {cleaned[7:]}"
        
        return phone
    
    except Exception:
        return phone

def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number"""
    try:
        if not phone:
            return False
        
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Check for valid Indian mobile number patterns
        # 10 digits starting with 6,7,8,9
        if len(cleaned) == 10 and cleaned[0] in '6789':
            return True
        
        # 11 digits starting with 0 followed by valid mobile number
        if len(cleaned) == 11 and cleaned.startswith('0') and cleaned[1] in '6789':
            return True
        
        # 12 digits starting with 91 (India country code)
        if len(cleaned) == 12 and cleaned.startswith('91') and cleaned[2] in '6789':
            return True
        
        return False
    
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate email address"""
    try:
        if not email:
            return True  # Email is optional
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    except Exception:
        return False

def format_date(date_input: Any) -> str:
    """Format date for display"""
    try:
        if pd.isna(date_input) or not date_input:
            return ""
        
        if isinstance(date_input, str):
            # Try to parse string date
            try:
                parsed_date = pd.to_datetime(date_input).date()
                return parsed_date.strftime("%d-%m-%Y")
            except:
                return date_input
        
        elif isinstance(date_input, (date, datetime)):
            if isinstance(date_input, datetime):
                date_input = date_input.date()
            return date_input.strftime("%d-%m-%Y")
        
        elif isinstance(date_input, pd.Timestamp):
            return date_input.strftime("%d-%m-%Y")
        
        return str(date_input)
    
    except Exception:
        return str(date_input) if date_input else ""

def format_datetime(dt_input: Any) -> str:
    """Format datetime for display"""
    try:
        if pd.isna(dt_input) or not dt_input:
            return ""
        
        if isinstance(dt_input, str):
            try:
                parsed_dt = pd.to_datetime(dt_input)
                return parsed_dt.strftime("%d-%m-%Y %I:%M %p")
            except:
                return dt_input
        
        elif isinstance(dt_input, datetime):
            return dt_input.strftime("%d-%m-%Y %I:%M %p")
        
        elif isinstance(dt_input, pd.Timestamp):
            return dt_input.strftime("%d-%m-%Y %I:%M %p")
        
        return str(dt_input)
    
    except Exception:
        return str(dt_input) if dt_input else ""

def calculate_age(birth_date: Any) -> Optional[int]:
    """Calculate age from birth date"""
    try:
        if pd.isna(birth_date) or not birth_date:
            return None
        
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date).date()
        elif isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        elif isinstance(birth_date, pd.Timestamp):
            birth_date = birth_date.date()
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        return age if age >= 0 else None
    
    except Exception:
        return None

def calculate_days_between(start_date: Any, end_date: Any = None) -> int:
    """Calculate days between two dates"""
    try:
        if not end_date:
            end_date = date.today()
        
        # Convert to date objects
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        elif isinstance(start_date, pd.Timestamp):
            start_date = start_date.date()
        
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        elif isinstance(end_date, pd.Timestamp):
            end_date = end_date.date()
        
        delta = end_date - start_date
        return delta.days
    
    except Exception:
        return 0

def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """Format percentage value"""
    try:
        if pd.isna(value):
            return "0%"
        
        return f"{value:.{decimal_places}f}%"
    
    except Exception:
        return "0%"

def clean_text(text: str) -> str:
    """Clean and format text input"""
    try:
        if not text:
            return ""
        
        # Strip whitespace and convert to proper case
        cleaned = text.strip()
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    except Exception:
        return text

def validate_positive_number(value: Any) -> bool:
    """Validate if value is a positive number"""
    try:
        if pd.isna(value):
            return False
        
        num = float(value)
        return num > 0
    
    except (ValueError, TypeError):
        return False

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """Safely divide two numbers"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    
    except (ValueError, TypeError, ZeroDivisionError):
        return default

def get_dashboard_metrics(db_manager):
    """Get dashboard metrics with error handling"""
    try:
        return db_manager.get_dashboard_metrics()
    except Exception as e:
        print(f"Error getting dashboard metrics: {str(e)}")
        return {
            'total_students': 0,
            'active_batches': 0,
            'monthly_revenue': 0,
            'pending_fees': 0,
            'pending_count': 0,
            'student_growth': 0,
            'batch_growth': 0,
            'revenue_growth': 0
        }

def format_student_name(first_name: str, last_name: str = "") -> str:
    """Format student name properly"""
    try:
        name_parts = []
        
        if first_name:
            name_parts.append(clean_text(first_name).title())
        
        if last_name:
            name_parts.append(clean_text(last_name).title())
        
        return " ".join(name_parts)
    
    except Exception:
        return f"{first_name} {last_name}".strip()

def calculate_fee_status(total_fee: float, paid_amount: float, due_date: Any = None) -> dict:
    """Calculate fee status and related information"""
    try:
        pending_amount = max(0, total_fee - paid_amount)
        is_paid = pending_amount <= 0
        
        status_info = {
            'pending_amount': pending_amount,
            'is_paid': is_paid,
            'payment_percentage': safe_divide(paid_amount, total_fee) * 100,
            'status': 'Paid' if is_paid else 'Pending'
        }
        
        # Calculate overdue status if due date is provided
        if due_date and not is_paid:
            try:
                if isinstance(due_date, str):
                    due_date = pd.to_datetime(due_date).date()
                elif isinstance(due_date, datetime):
                    due_date = due_date.date()
                elif isinstance(due_date, pd.Timestamp):
                    due_date = due_date.date()
                
                days_overdue = calculate_days_between(due_date, date.today())
                
                if days_overdue > 0:
                    status_info['status'] = 'Overdue'
                    status_info['days_overdue'] = days_overdue
                else:
                    status_info['days_until_due'] = abs(days_overdue)
            
            except Exception:
                pass
        
        return status_info
    
    except Exception:
        return {
            'pending_amount': 0,
            'is_paid': True,
            'payment_percentage': 100,
            'status': 'Unknown'
        }

def generate_student_id(student_name: str, admission_date: Any = None) -> str:
    """Generate unique student ID"""
    try:
        # Clean name for ID
        name_part = ''.join(c.upper() for c in student_name if c.isalpha())[:3]
        
        # Get year from admission date
        if admission_date:
            if isinstance(admission_date, str):
                year = pd.to_datetime(admission_date).year
            elif isinstance(admission_date, (date, datetime)):
                year = admission_date.year
            elif isinstance(admission_date, pd.Timestamp):
                year = admission_date.year
            else:
                year = date.today().year
        else:
            year = date.today().year
        
        # Generate timestamp-based suffix
        timestamp = datetime.now().strftime("%m%d")
        
        return f"{name_part}{year}{timestamp}"
    
    except Exception:
        return f"STU{datetime.now().strftime('%Y%m%d%H%M%S')}"

def calculate_attendance_rate(present_count: int, total_sessions: int) -> float:
    """Calculate attendance rate percentage"""
    try:
        if total_sessions <= 0:
            return 0.0
        
        return min(100.0, (present_count / total_sessions) * 100)
    
    except Exception:
        return 0.0

def get_grade_from_percentage(percentage: float) -> str:
    """Get grade based on percentage"""
    try:
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"
    
    except Exception:
        return "N/A"

def format_test_score(marks_obtained: float, total_marks: float) -> str:
    """Format test score for display"""
    try:
        percentage = (marks_obtained / total_marks) * 100 if total_marks > 0 else 0
        grade = get_grade_from_percentage(percentage)
        
        return f"{marks_obtained:.0f}/{total_marks:.0f} ({percentage:.1f}% - {grade})"
    
    except Exception:
        return f"{marks_obtained}/{total_marks}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    try:
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove extra spaces and dots
        sanitized = re.sub(r'\.+', '.', sanitized)
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:90] + ('.' + ext if ext else '')
        
        return sanitized
    
    except Exception:
        return filename

def calculate_working_days(start_date: Any, end_date: Any, exclude_weekends: bool = True) -> int:
    """Calculate working days between two dates"""
    try:
        # Convert to date objects
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        elif isinstance(start_date, pd.Timestamp):
            start_date = start_date.date()
        
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        elif isinstance(end_date, pd.Timestamp):
            end_date = end_date.date()
        
        if exclude_weekends:
            # Count weekdays only
            total_days = (end_date - start_date).days + 1
            weekdays = 0
            
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    weekdays += 1
                current_date += pd.Timedelta(days=1)
            
            return weekdays
        else:
            return (end_date - start_date).days + 1
    
    except Exception:
        return 0

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable format"""
    try:
        if minutes < 60:
            return f"{minutes} min"
        elif minutes < 1440:  # Less than a day
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours} hr"
            else:
                return f"{hours} hr {mins} min"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            if hours == 0:
                return f"{days} day"
            else:
                return f"{days} day {hours} hr"
    
    except Exception:
        return f"{minutes} min"
