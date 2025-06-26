"""
Configuration settings for EduCRM - Coaching Institute Management System
Contains application-wide settings and constants
"""

import os
from typing import Dict, List

# Application Information
APP_CONFIG = {
    "name": "EduCRM",
    "version": "2.0.0",
    "description": "Comprehensive Coaching Institute Management System",
    "author": "EduCRM Development Team",
    "contact_email": "support@educrm.com"
}

# Database Configuration
DATABASE_CONFIG = {
    "nocodb_base_url": os.getenv("NOCODB_BASE_URL", "http://localhost:8080"),
    "nocodb_api_token": os.getenv("NOCODB_API_TOKEN", ""),
    "nocodb_workspace_id": os.getenv("NOCODB_WORKSPACE_ID", ""),
    "nocodb_base_id": os.getenv("NOCODB_BASE_ID", ""),
    "connection_timeout": 30,
    "retry_attempts": 3
}

# Authentication Configuration
AUTH_CONFIG = {
    "admin_username": os.getenv("ADMIN_USERNAME", "admin"),
    "admin_password": os.getenv("ADMIN_PASSWORD", "educrm2024"),
    "session_timeout": 3600,  # 1 hour in seconds
    "max_login_attempts": 5
}

# WhatsApp Configuration
WHATSAPP_CONFIG = {
    "base_url": "https://wa.me/",
    "web_url": "https://web.whatsapp.com/send",
    "default_country_code": "91",  # India
    "message_length_limit": 1000
}

# Fee Management Configuration
FEE_CONFIG = {
    "currency_symbol": "₹",
    "default_late_fee_percentage": 5.0,
    "grace_period_days": 7,
    "overdue_threshold_days": 30,
    "reminder_intervals": [7, 3, 1]  # Days before due date to send reminders
}

# Performance Tracking Configuration
PERFORMANCE_CONFIG = {
    "default_passing_marks": 50.0,
    "grade_boundaries": {
        "A+": 90,
        "A": 80,
        "B+": 70,
        "B": 60,
        "C": 50,
        "D": 40,
        "F": 0
    },
    "attendance_minimum": 75.0  # Minimum attendance percentage required
}

# Category Configuration
CATEGORY_CONFIG = {
    "default_categories": [
        {
            "name": "NEET Preparation",
            "description": "Medical entrance exam preparation",
            "color": "#4CAF50"
        },
        {
            "name": "JEE Main & Advanced", 
            "description": "Engineering entrance exam preparation",
            "color": "#2196F3"
        },
        {
            "name": "UPSC Preparation",
            "description": "Civil services exam preparation", 
            "color": "#FF9800"
        }
    ]
}

# Batch Configuration
BATCH_CONFIG = {
    "default_capacity": 30,
    "schedule_formats": [
        "Mon-Fri 9AM-12PM",
        "Mon-Fri 2PM-5PM", 
        "Weekends 9AM-1PM",
        "Mon,Wed,Fri 6PM-8PM",
        "Tue,Thu,Sat 6PM-8PM"
    ],
    "duration_options": [
        "3 months",
        "6 months", 
        "1 year",
        "2 years"
    ]
}

# Communication Templates
MESSAGE_TEMPLATES = {
    "fee_reminder_gentle": """Dear {student_name},

This is a gentle reminder that your fee payment of ₹{pending_amount} for {batch_name} is pending.

Please make the payment at your earliest convenience to avoid any interruption in your classes.

Due Date: {due_date}

Thank you for your cooperation!

Best regards,
EduCRM Team""",

    "fee_reminder_urgent": """Dear Parent,

URGENT REMINDER: The fee payment of ₹{pending_amount} for your ward {student_name} ({batch_name}) is overdue.

Please clear the dues immediately to ensure uninterrupted classes.

Original Due Date: {due_date}

For any queries, please contact us immediately.

EduCRM Team""",

    "fee_reminder_final": """FINAL NOTICE

Dear Parent,

Despite previous reminders, the fee of ₹{pending_amount} for {student_name} ({batch_name}) remains unpaid.

Please clear the outstanding amount within 24 hours to avoid suspension of classes.

Due Date: {due_date}

Contact our office immediately to resolve this matter.

EduCRM Administration""",

    "payment_confirmation": """✅ PAYMENT CONFIRMATION

Dear Parent,

We acknowledge the receipt of ₹{amount_paid} for {student_name}'s fee payment on {payment_date}.

{balance_message}

Thank you for your prompt payment!

Best regards,
EduCRM Team""",

    "exam_notice": """📝 EXAM NOTICE

Dear {student_name},

This is to inform you about the upcoming {exam_name}.

Batch: {batch_name}
Exam Date: {exam_date}
Time: {exam_time}
Venue: {venue}

Please prepare well and be present on time.

Best of luck!

EduCRM Team""",

    "holiday_notice": """🏖️ HOLIDAY NOTICE

Dear Students,

Our institute will be closed for {holiday_name}.

{date_info}

Classes will resume as per regular schedule after the holiday.

Stay safe and enjoy the break!

EduCRM Team""",

    "admission_welcome": """🎉 WELCOME TO EduCRM

Dear {student_name},

Congratulations! Your admission to {batch_name} has been confirmed.

Classes start from: {start_date}
Batch Timing: {schedule}
Instructor: {instructor}

We are excited to have you as part of our learning community. Our experienced faculty and comprehensive study material will help you achieve your goals.

For any queries, contact us at: {contact_number}

Best wishes for your academic journey!

EduCRM Team""",

    "batch_announcement": """📢 BATCH ANNOUNCEMENT - {batch_name}

{announcement}

Date: {date}

For any clarifications, please contact the institute.

EduCRM Team"""
}

# Report Configuration
REPORT_CONFIG = {
    "export_formats": ["Excel", "PDF", "CSV"],
    "max_records_per_export": 10000,
    "default_date_format": "%d-%m-%Y",
    "default_datetime_format": "%d-%m-%Y %I:%M %p"
}

# System Configuration
SYSTEM_CONFIG = {
    "max_file_upload_size": 5,  # MB
    "session_cleanup_interval": 24,  # hours
    "backup_retention_days": 30,
    "log_retention_days": 90,
    "max_concurrent_users": 10
}

# Validation Rules
VALIDATION_RULES = {
    "student_name": {
        "min_length": 2,
        "max_length": 100,
        "pattern": r"^[a-zA-Z\s.]+$"
    },
    "phone_number": {
        "min_length": 10,
        "max_length": 15,
        "pattern": r"^[0-9+\-\s()]+$"
    },
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    },
    "fee_amount": {
        "min_value": 0,
        "max_value": 1000000
    },
    "marks": {
        "min_value": 0,
        "max_value": 1000
    }
}

# Error Messages
ERROR_MESSAGES = {
    "database_connection": "Unable to connect to database. Please check your connection and try again.",
    "invalid_credentials": "Invalid username or password. Please try again.",
    "session_expired": "Your session has expired. Please login again.",
    "invalid_phone": "Please enter a valid phone number (10 digits).",
    "invalid_email": "Please enter a valid email address.",
    "invalid_amount": "Please enter a valid amount.",
    "required_field": "This field is required.",
    "duplicate_entry": "This record already exists.",
    "insufficient_permissions": "You don't have permission to perform this action.",
    "export_failed": "Failed to export data. Please try again.",
    "file_too_large": "File size exceeds maximum limit.",
    "invalid_date": "Please enter a valid date.",
    "batch_full": "This batch has reached maximum capacity.",
    "student_not_found": "Student not found.",
    "payment_failed": "Payment recording failed. Please try again."
}

# Success Messages
SUCCESS_MESSAGES = {
    "student_added": "Student added successfully!",
    "student_updated": "Student information updated successfully!",
    "payment_recorded": "Payment recorded successfully!",
    "message_sent": "Messages sent successfully!",
    "batch_created": "Batch created successfully!",
    "category_added": "Category added successfully!",
    "export_completed": "Data exported successfully!",
    "settings_saved": "Settings saved successfully!",
    "backup_created": "Backup created successfully!"
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "refresh_interval": 300,  # seconds
    "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    "metrics_cards": [
        "total_students",
        "active_batches", 
        "monthly_revenue",
        "pending_fees"
    ],
    "recent_activities_limit": 10,
    "pending_tasks_limit": 5
}

# Navigation Configuration
NAVIGATION_CONFIG = {
    "sidebar_pages": [
        {
            "name": "Dashboard",
            "icon": "🏠",
            "page": "app.py"
        },
        {
            "name": "Student Management", 
            "icon": "👨‍🎓",
            "page": "pages/1_Student_Management.py"
        },
        {
            "name": "Batch Management",
            "icon": "📚", 
            "page": "pages/2_Batch_Management.py"
        },
        {
            "name": "Communication",
            "icon": "📱",
            "page": "pages/3_Communication.py"
        },
        {
            "name": "Fee Management",
            "icon": "💰",
            "page": "pages/4_Fee_Management.py"
        },
        {
            "name": "Performance Tracking",
            "icon": "📈",
            "page": "pages/5_Performance_Tracking.py"
        },
        {
            "name": "Reports",
            "icon": "📊",
            "page": "pages/6_Reports.py"
        }
    ]
}

# Table Schema Definitions for NocoDB
DATABASE_SCHEMA = {
    "categories": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "name", "type": "SingleLineText", "required": True, "unique": True},
            {"name": "description", "type": "LongText"},
            {"name": "color", "type": "SingleLineText", "default": "#1f77b4"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "batches": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "name", "type": "SingleLineText", "required": True},
            {"name": "category", "type": "SingleLineText", "required": True},
            {"name": "start_date", "type": "Date", "required": True},
            {"name": "end_date", "type": "Date"},
            {"name": "capacity", "type": "Number", "default": 30},
            {"name": "fee", "type": "Currency"},
            {"name": "schedule", "type": "SingleLineText"},
            {"name": "instructor", "type": "SingleLineText"},
            {"name": "description", "type": "LongText"},
            {"name": "whatsapp_group_link", "type": "URL"},
            {"name": "status", "type": "SingleSelect", "options": ["Active", "Upcoming", "Completed", "Cancelled"], "default": "Active"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "students": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "full_name", "type": "SingleLineText", "required": True},
            {"name": "parent_phone", "type": "PhoneNumber", "required": True},
            {"name": "student_phone", "type": "PhoneNumber"},
            {"name": "email", "type": "Email"},
            {"name": "address", "type": "LongText"},
            {"name": "date_of_birth", "type": "Date"},
            {"name": "category", "type": "SingleLineText", "required": True},
            {"name": "batch", "type": "SingleLineText", "required": True},
            {"name": "batch_id", "type": "Number"},
            {"name": "total_fee", "type": "Currency", "default": 0},
            {"name": "paid_amount", "type": "Currency", "default": 0},
            {"name": "discount", "type": "Currency", "default": 0},
            {"name": "fee_due_date", "type": "Date"},
            {"name": "admission_date", "type": "Date", "default": "today"},
            {"name": "status", "type": "SingleSelect", "options": ["Active", "Inactive", "Completed", "Dropped"], "default": "Active"},
            {"name": "notes", "type": "LongText"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "tests": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "name", "type": "SingleLineText", "required": True},
            {"name": "subject", "type": "SingleLineText"},
            {"name": "date", "type": "Date", "required": True},
            {"name": "max_marks", "type": "Number", "required": True},
            {"name": "category", "type": "SingleLineText", "required": True},
            {"name": "batch", "type": "SingleLineText", "required": True},
            {"name": "batch_id", "type": "Number"},
            {"name": "description", "type": "LongText"},
            {"name": "status", "type": "SingleSelect", "options": ["Scheduled", "Completed", "Cancelled"], "default": "Scheduled"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "test_scores": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "test_id", "type": "Number", "required": True},
            {"name": "student_id", "type": "Number", "required": True},
            {"name": "marks_obtained", "type": "Number", "required": True},
            {"name": "attendance", "type": "SingleSelect", "options": ["Present", "Absent"], "default": "Present"},
            {"name": "remarks", "type": "LongText"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "payments": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "student_id", "type": "Number", "required": True},
            {"name": "amount", "type": "Currency", "required": True},
            {"name": "payment_method", "type": "SingleSelect", "options": ["Cash", "UPI", "Bank Transfer", "Cheque", "Card", "Online"], "default": "Cash"},
            {"name": "payment_date", "type": "Date", "required": True},
            {"name": "transaction_reference", "type": "SingleLineText"},
            {"name": "notes", "type": "LongText"},
            {"name": "late_fee", "type": "Currency", "default": 0},
            {"name": "discount", "type": "Currency", "default": 0},
            {"name": "status", "type": "SingleSelect", "options": ["Completed", "Pending", "Failed", "Refunded"], "default": "Completed"},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "message_templates": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "name", "type": "SingleLineText", "required": True},
            {"name": "category", "type": "SingleSelect", "options": ["General", "Fee Reminder", "Exam Notice", "Holiday Notice", "Admission"], "default": "General"},
            {"name": "type", "type": "SingleLineText"},
            {"name": "content", "type": "LongText", "required": True},
            {"name": "is_active", "type": "Checkbox", "default": True},
            {"name": "usage_count", "type": "Number", "default": 0},
            {"name": "created_at", "type": "DateTime", "default": "now()"},
            {"name": "updated_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "communication_logs": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "timestamp", "type": "DateTime", "required": True},
            {"name": "recipient_count", "type": "Number", "required": True},
            {"name": "message_preview", "type": "LongText"},
            {"name": "template_used", "type": "SingleLineText"},
            {"name": "activity_type", "type": "SingleSelect", "options": ["whatsapp_message", "email", "sms", "announcement"], "default": "whatsapp_message"},
            {"name": "status", "type": "SingleSelect", "options": ["Success", "Failed", "Partial"], "default": "Success"},
            {"name": "created_at", "type": "DateTime", "default": "now()"}
        ]
    },
    "activities": {
        "fields": [
            {"name": "id", "type": "AutoNumber", "primary": True},
            {"name": "description", "type": "LongText", "required": True},
            {"name": "timestamp", "type": "DateTime", "required": True},
            {"name": "activity_type", "type": "SingleSelect", "options": ["system", "user", "payment", "enrollment", "communication", "test"], "default": "system"},
            {"name": "user_id", "type": "SingleLineText"},
            {"name": "metadata", "type": "JSON"},
            {"name": "created_at", "type": "DateTime", "default": "now()"}
        ]
    }
}

# API Rate Limiting
API_CONFIG = {
    "rate_limit_per_minute": 60,
    "bulk_operation_limit": 100,
    "export_size_limit": 50000  # records
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_sms": False,
    "enable_email": False, 
    "enable_whatsapp_api": False,  # Using manual links for now
    "enable_online_payments": False,
    "enable_multi_language": False,
    "enable_mobile_app": False,
    "enable_parent_portal": False,
    "enable_advanced_analytics": True,
    "enable_bulk_operations": True,
    "enable_data_export": True
}

# Cache Configuration
CACHE_CONFIG = {
    "enable_caching": True,
    "cache_ttl": 300,  # seconds
    "max_cache_size": 100  # MB
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "logs/educrm.log",
    "max_log_size": 10,  # MB
    "backup_count": 5
}

# Security Configuration
SECURITY_CONFIG = {
    "password_min_length": 8,
    "password_require_special_chars": True,
    "session_cookie_secure": True,
    "session_cookie_httponly": True,
    "csrf_protection": True,
    "xss_protection": True
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    "enable_browser_notifications": True,
    "enable_sound_alerts": False,
    "notification_timeout": 5000,  # milliseconds
    "max_notifications": 5
}

# Theme Configuration
THEME_CONFIG = {
    "primary_color": "#1f77b4",
    "background_color": "#ffffff", 
    "secondary_background_color": "#f0f2f6",
    "text_color": "#262730",
    "font_family": "sans serif"
}

# Get environment-specific configuration
def get_config():
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    config = {
        "app": APP_CONFIG,
        "database": DATABASE_CONFIG,
        "auth": AUTH_CONFIG,
        "whatsapp": WHATSAPP_CONFIG,
        "fee": FEE_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "category": CATEGORY_CONFIG,
        "batch": BATCH_CONFIG,
        "message_templates": MESSAGE_TEMPLATES,
        "report": REPORT_CONFIG,
        "system": SYSTEM_CONFIG,
        "validation": VALIDATION_RULES,
        "errors": ERROR_MESSAGES,
        "success": SUCCESS_MESSAGES,
        "dashboard": DASHBOARD_CONFIG,
        "navigation": NAVIGATION_CONFIG,
        "database_schema": DATABASE_SCHEMA,
        "api": API_CONFIG,
        "features": FEATURE_FLAGS,
        "cache": CACHE_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "notifications": NOTIFICATION_CONFIG,
        "theme": THEME_CONFIG
    }
    
    # Environment-specific overrides
    if env == "production":
        config["system"]["max_concurrent_users"] = 50
        config["api"]["rate_limit_per_minute"] = 120
        config["cache"]["cache_ttl"] = 600
        config["logging"]["log_level"] = "WARNING"
    
    elif env == "testing":
        config["database"]["connection_timeout"] = 10
        config["auth"]["session_timeout"] = 1800  # 30 minutes
        config["logging"]["log_level"] = "DEBUG"
    
    return config

# Validation functions
def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    import re
    pattern = VALIDATION_RULES["phone_number"]["pattern"]
    return bool(re.match(pattern, phone)) if phone else False

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = VALIDATION_RULES["email"]["pattern"]
    return bool(re.match(pattern, email)) if email else True  # Optional field

def validate_student_name(name: str) -> bool:
    """Validate student name"""
    import re
    if not name:
        return False
    
    rules = VALIDATION_RULES["student_name"]
    if len(name) < rules["min_length"] or len(name) > rules["max_length"]:
        return False
    
    return bool(re.match(rules["pattern"], name))

def validate_fee_amount(amount: float) -> bool:
    """Validate fee amount"""
    rules = VALIDATION_RULES["fee_amount"]
    return rules["min_value"] <= amount <= rules["max_value"]

def validate_marks(marks: float, max_marks: float) -> bool:
    """Validate test marks"""
    rules = VALIDATION_RULES["marks"]
    return rules["min_value"] <= marks <= min(max_marks, rules["max_value"])

# Helper functions
def get_default_categories():
    """Get default categories for initialization"""
    return CATEGORY_CONFIG["default_categories"]

def get_grade_from_percentage(percentage: float) -> str:
    """Get grade based on percentage"""
    boundaries = PERFORMANCE_CONFIG["grade_boundaries"]
    for grade, min_percentage in boundaries.items():
        if percentage >= min_percentage:
            return grade
    return "F"

def get_fee_reminder_template(reminder_type: str) -> str:
    """Get fee reminder template by type"""
    template_key = f"fee_reminder_{reminder_type}"
    return MESSAGE_TEMPLATES.get(template_key, MESSAGE_TEMPLATES["fee_reminder_gentle"])

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature, False)

def get_chart_colors():
    """Get chart colors for visualizations"""
    return DASHBOARD_CONFIG["chart_colors"]

def get_database_schema(table_name: str) -> dict:
    """Get database schema for a specific table"""
    return DATABASE_SCHEMA.get(table_name, {})

def get_error_message(error_code: str) -> str:
    """Get error message by code"""
    return ERROR_MESSAGES.get(error_code, "An unexpected error occurred.")

def get_success_message(success_code: str) -> str:
    """Get success message by code"""
    return SUCCESS_MESSAGES.get(success_code, "Operation completed successfully.")

# Export main configuration
def get_app_config():
    """Get main application configuration"""
    return get_config()

