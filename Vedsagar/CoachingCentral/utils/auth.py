import streamlit as st
import hashlib
import os
from typing import Optional

class AuthManager:
    """
    Authentication manager for the EduCRM system
    Handles user login and session management
    """
    
    def __init__(self):
        # Default admin credentials - can be overridden via environment variables
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password_hash = self._hash_password(os.getenv("ADMIN_PASSWORD", "educrm2024"))
        
        # Session settings
        self.session_timeout = 3600  # 1 hour in seconds
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if username == self.admin_username:
            password_hash = self._hash_password(password)
            return password_hash == self.admin_password_hash
        return False
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if 'authenticated' not in st.session_state:
            return False
        
        if 'login_time' not in st.session_state:
            return False
        
        # Check session timeout
        import time
        current_time = time.time()
        login_time = st.session_state.get('login_time', 0)
        
        if current_time - login_time > self.session_timeout:
            # Session expired
            st.session_state.authenticated = False
            st.session_state.pop('login_time', None)
            return False
        
        return st.session_state.authenticated
    
    def login_user(self, username: str) -> None:
        """Log in user and set session variables"""
        import time
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.login_time = time.time()
    
    def logout_user(self) -> None:
        """Log out user and clear session"""
        st.session_state.authenticated = False
        st.session_state.pop('username', None)
        st.session_state.pop('login_time', None)
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged-in user"""
        if self.is_session_valid():
            return st.session_state.get('username')
        return None

# Global auth manager instance
auth_manager = AuthManager()

def authenticate_user():
    """
    Display login form and handle authentication
    This function should be called at the beginning of each page
    """
    if not auth_manager.is_session_valid():
        st.title("🔐 EduCRM Login")
        st.markdown("Welcome to the Coaching Institute Management System")
        
        with st.form("login_form"):
            st.subheader("Admin Login")
            
            username = st.text_input("Username", placeholder="Enter admin username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                elif auth_manager.verify_credentials(username, password):
                    auth_manager.login_user(username)
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        # Login instructions
        with st.expander("🔑 Default Login Credentials"):
            st.code(f"""
Username: {auth_manager.admin_username}
Password: educrm2024

Note: You can change these credentials using environment variables:
- ADMIN_USERNAME
- ADMIN_PASSWORD
            """)
        
        st.markdown("---")
        st.markdown("### 🏫 About EduCRM")
        st.info("""
        EduCRM is a comprehensive coaching institute management system that helps you:
        
        📚 **Manage Students & Batches**
        - Track student enrollments and progress
        - Organize batches by categories (NEET, JEE, UPSC, etc.)
        
        💰 **Handle Fees & Payments**
        - Track fee collections and pending amounts
        - Generate payment reminders
        
        📱 **WhatsApp Communication**
        - Send batch-wise messages
        - Automated fee reminders
        - Template-based messaging
        
        📊 **Performance Tracking**
        - Record test scores and performance
        - Generate detailed reports
        - Track student progress over time
        
        📈 **Analytics & Reports**
        - Dashboard with key metrics
        - Financial and academic reports
        - Export data to Excel
        """)
    
    return auth_manager.is_session_valid()

def require_auth():
    """
    Decorator/function to require authentication
    Returns True if authenticated, False otherwise
    """
    return auth_manager.is_session_valid()

def get_current_user() -> Optional[str]:
    """Get the current authenticated user"""
    return auth_manager.get_current_user()

def logout():
    """Logout current user"""
    auth_manager.logout_user()
