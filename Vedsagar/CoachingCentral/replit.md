# EduCRM - Coaching Institute Management System

## Overview

EduCRM is a comprehensive Coaching Institute Management System built with Streamlit as a web-based dashboard application. The system provides complete management capabilities for educational institutions including student management, batch organization, fee tracking, performance monitoring, and communication tools. The application is designed as a single-page application with multiple tabs for different functional areas.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit (Python-based web framework)
- **UI Components**: Multi-tab interface with responsive design
- **Visualization**: Plotly for charts and graphs
- **Styling**: Custom CSS via Streamlit theming

### Backend Architecture
- **Database Integration**: NocoDB as the primary database backend
- **Authentication**: Session-based authentication with hash-based password storage
- **API Communication**: RESTful API calls to NocoDB endpoints
- **Data Processing**: Pandas for data manipulation and analysis

### Application Structure
- **Main App**: `app.py` serves as the dashboard entry point
- **Pages**: Modular page structure using Streamlit's multi-page format
- **Utilities**: Helper modules for database operations, authentication, and WhatsApp integration
- **Configuration**: Centralized settings management

## Key Components

### 1. Authentication System (`utils/auth.py`)
- SHA-256 password hashing
- Session timeout management (1-hour default)
- Environment variable support for credentials
- Default admin credentials: username="admin", password="educrm2024"

### 2. Database Layer (`utils/database.py`)
- NocoDB integration with API token authentication
- Table mapping for categories, batches, students, tests, payments, etc.
- Connection validation and error handling
- Excel export functionality for reports

### 3. Communication Module (`utils/whatsapp.py`)
- WhatsApp link generation for direct messaging
- Phone number formatting and validation
- Support for both mobile and web WhatsApp interfaces
- Message template system

### 4. Core Pages
- **Student Management**: Add, view, search, and edit student records
- **Batch Management**: Category and batch creation with analytics
- **Communication Center**: WhatsApp messaging and template management
- **Fee Management**: Payment tracking and fee collection overview
- **Performance Tracking**: Test score recording and student analytics
- **Reports**: Comprehensive reporting and analytics dashboard

### 5. Helper Utilities (`utils/helpers.py`)
- Currency formatting (Indian Rupees with crore/lakh notation)
- Phone number formatting
- Data validation functions
- Dashboard metrics calculation

## Data Flow

### Student Registration Flow
1. Admin adds student via Student Management page
2. Student data validated and stored in NocoDB
3. Student assigned to batch and category
4. Automatic fee structure application

### Communication Flow
1. Admin selects recipients (individual/batch/custom)
2. Message template selected or custom message created
3. WhatsApp links generated with pre-filled messages
4. Communication logged in database for tracking

### Fee Management Flow
1. Fee structures defined per batch/category
2. Payment records maintained per student
3. Automatic overdue calculation and tracking
4. Reminder system with configurable intervals

### Performance Tracking Flow
1. Tests created and linked to batches
2. Student scores recorded manually
3. Performance analytics generated
4. Progress reports created for students/batches

## External Dependencies

### Core Dependencies
- **Streamlit**: Web framework for the dashboard interface
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **OpenPyXL**: Excel file operations for reports
- **Requests**: HTTP client for NocoDB API calls

### Database Integration
- **NocoDB**: Primary database backend (self-hosted or cloud)
- **RESTful API**: Communication via HTTP/JSON
- **Environment Variables**: Configuration management

### Communication Integration
- **WhatsApp**: URL-based integration (no API key required)
- **Template System**: Pre-defined message templates
- **Contact Management**: Phone number validation and formatting

## Deployment Strategy

### Replit Deployment
- **Runtime**: Python 3.11 with Nix package manager
- **Port Configuration**: 5000 (configurable)
- **Auto-scaling**: Enabled for production deployment
- **Environment**: Stable 24.05 Nix channel

### Configuration Management
- **Settings File**: `config/settings.py` for centralized configuration
- **Environment Variables**: Database credentials, admin passwords
- **Streamlit Config**: Custom theming and server settings

### Database Setup Requirements
- NocoDB instance (local or cloud)
- API token generation
- Workspace and base ID configuration
- Table structure initialization

### Security Considerations
- Password hashing (SHA-256)
- Session management with timeout
- Environment variable protection for sensitive data
- API token-based database authentication

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 26, 2025. Initial setup