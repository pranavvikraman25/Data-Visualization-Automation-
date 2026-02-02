"""
Application Configuration & Constants
Centralized settings for the Streamlit app
"""

from enum import Enum
from typing import Dict

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_TITLE = "Component Management & Visualization"
APP_DESCRIPTION = "Streamline maintenance timing and resource allocation"
APP_VERSION = "1.0.0"
APP_AUTHOR = "KONE Maintenance Team"

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================

PAGE_CONFIG = {
    "page_title": "Component Management Dashboard",
    "page_icon": "🔧",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ============================================================================
# COLOR SCHEME
# ============================================================================

COLORS = {
    "primary": "#2E7D9E",        # Primary blue
    "secondary": "#F24236",       # Secondary red
    "accent": "#FDB833",          # Accent yellow
    "dark": "#1A1A1A",            # Dark gray
    "light": "#F5F5F5",           # Light gray
    "success": "#4CAF50",         # Success green
    "warning": "#FF9800",         # Warning orange
    "error": "#F44336",           # Error red
}

# ============================================================================
# UI TEXT & LABELS
# ============================================================================

UI_LABELS = {
    "upload_title": "📁 Data Management",
    "upload_button": "Upload Excel File",
    "upload_help": "Upload your component data in Excel format",
    
    "view_title": "👁️ View Options",
    "view_selection": "Select View",
    "view_component_selection": "Component Selection",
    "view_data_analysis": "Data Analysis",
    "view_summary_report": "Summary Report",
    
    "export_title": "💾 Export Options",
    "export_csv": "📥 Download CSV",
    
    "main_title": "🔧 Component Management & Visualization",
    "main_subtitle": "Streamline maintenance timing and resource allocation",
    
    "step1_title": "Step 1: Select Main Component",
    "step1_subtitle": "Available Components",
    "step1_selected": "Selected",
    
    "step2_title": "Step 2: Select Sub-Components",
    "step2_subtitle": "Choose sub-components (default: first one selected)",
    "step2_count": "Selected Count",
    
    "step3_title": "Step 3: Preview Selected Data",
    "step3_subtitle": "Summary Statistics",
    
    "analysis_title": "Data Analysis & Insights",
    "analysis_table": "Table View",
    "analysis_time": "Time Analysis",
    "analysis_manpower": "Manpower Analysis",
    "analysis_breakdown": "Component Breakdown",
}

# ============================================================================
# METRIC LABELS
# ============================================================================

METRIC_LABELS = {
    "total_components": "Total Components",
    "total_sub_components": "Total Sub-Components",
    "total_manpower": "Total Manpower Required",
    "total_data_points": "Data Points",
    "avg_manpower": "Average Manpower",
    "max_manpower": "Max Manpower",
    "total_time": "Total Time",
    "prep_time": "Preparation Time",
    "activity_time": "Activity Time",
}

# ============================================================================
# VALIDATION SETTINGS
# ============================================================================

REQUIRED_COLUMNS = [
    'S.no',
    'Component',
    'Component.1',
    'Preparation/Finalization (h:mm:ss)',
    'Activity (h:mm:ss)',
    'Total time (h:mm:ss)',
    'No of man power'
]

COLUMN_NAMES = {
    'S.no': 'S.no',
    'main_component': 'Component',
    'sub_component': 'Component.1',
    'prep_time': 'Preparation/Finalization (h:mm:ss)',
    'activity_time': 'Activity (h:mm:ss)',
    'total_time': 'Total time (h:mm:ss)',
    'manpower': 'No of man power',
}

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULTS = {
    "manpower_threshold": 2,
    "time_threshold_hours": 2.0,
    "max_upload_size_mb": 50,
    "decimal_places": 2,
}

# ============================================================================
# CHART SETTINGS
# ============================================================================

CHART_CONFIG = {
    "theme": "plotly_white",
    "height": 500,
    "show_legend": True,
    "animation_frame_duration": 500,
}

# ============================================================================
# TIME FORMAT SETTINGS
# ============================================================================

TIME_FORMAT = "HH:MM:SS"
TIME_REGEX = r"^([0-9]{2}):([0-5][0-9]):([0-5][0-9])$"

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

SIDEBAR_WIDTH = 25  # Percentage

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

PERFORMANCE = {
    "cache_ttl": 3600,  # Cache time-to-live in seconds
    "max_rows_display": 1000,  # Max rows to display without pagination
    "lazy_load": True,  # Enable lazy loading for large datasets
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "component_manager.log",
}

# ============================================================================
# ENUMS FOR TYPE SAFETY
# ============================================================================

class ViewMode(Enum):
    """Available view modes."""
    COMPONENT_SELECTION = "Component Selection"
    DATA_ANALYSIS = "Data Analysis"
    SUMMARY_REPORT = "Summary Report"

class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"

class TimeUnit(Enum):
    """Time unit options."""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"

# ============================================================================
# ADVANCED SETTINGS (For Future Use)
# ============================================================================

DATABASE_CONFIG = {
    "type": "sqlite",  # or "postgresql", "mysql"
    "host": "localhost",
    "port": 5432,
    "database": "components_db",
    "username": "admin",
    "password": "",  # Use environment variables in production
}

API_CONFIG = {
    "enabled": False,
    "port": 8000,
    "host": "0.0.0.0",
    "debug": False,
}

AUTH_CONFIG = {
    "enabled": False,
    "provider": "local",  # or "oauth", "saml"
    "session_timeout": 3600,  # 1 hour in seconds
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    "enable_export": True,
    "enable_charts": True,
    "enable_advanced_analytics": False,
    "enable_multi_user": False,
    "enable_database_sync": False,
    "enable_api": False,
    "enable_authentication": False,
    "enable_audit_logging": False,
}

# ============================================================================
# NOTIFICATION MESSAGES
# ============================================================================

MESSAGES = {
    "file_loaded": "✅ File loaded successfully!",
    "file_error": "❌ Error loading file",
    "no_data": "👈 Please upload an Excel file to get started",
    "no_selection": "⚠️ Please select a component and sub-components first",
    "export_success": "✅ File prepared for download",
    "validation_error": "❌ Data validation failed",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_color(color_name: str) -> str:
    """Get color hex value by name."""
    return COLORS.get(color_name, COLORS["primary"])

def get_label(label_key: str) -> str:
    """Get UI label by key."""
    return UI_LABELS.get(label_key, label_key)

def get_metric_label(metric_key: str) -> str:
    """Get metric label by key."""
    return METRIC_LABELS.get(metric_key, metric_key)

def get_message(message_key: str) -> str:
    """Get message by key."""
    return MESSAGES.get(message_key, message_key)

def is_feature_enabled(feature_name: str) -> bool:
    """Check if feature is enabled."""
    return FEATURES.get(f"enable_{feature_name}", False)

# ============================================================================
# ENVIRONMENT-SPECIFIC SETTINGS
# ============================================================================

ENVIRONMENTS = {
    "development": {
        "debug": True,
        "features": {
            "enable_advanced_analytics": True,
            "enable_api": True,
        }
    },
    "production": {
        "debug": False,
        "features": {
            "enable_advanced_analytics": True,
            "enable_api": True,
        }
    },
    "testing": {
        "debug": True,
        "features": {
            "enable_advanced_analytics": True,
            "enable_api": False,
        }
    }
}
