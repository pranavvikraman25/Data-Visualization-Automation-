"""
Data Processing Module
Handles data loading, validation, and transformation
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta

# ============================================================================
# COLUMN VALIDATION
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

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

def validate_excel_structure(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that Excel file has required columns.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
    
    return len(errors) == 0, errors

def validate_time_format(time_str: str) -> bool:
    """
    Validate that time is in HH:MM:SS format.
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if pd.isna(time_str):
        return False
    
    try:
        parts = str(time_str).split(':')
        if len(parts) != 3:
            return False
        
        hours, minutes, seconds = map(int, parts)
        
        if hours < 0 or minutes < 0 or minutes > 59 or seconds < 0 or seconds > 59:
            return False
        
        return True
    except (ValueError, AttributeError):
        return False

def validate_manpower(value) -> bool:
    """Validate that manpower is a positive integer."""
    try:
        val = int(value)
        return val > 0
    except (ValueError, TypeError):
        return False

# ============================================================================
# TIME CONVERSION UTILITIES
# ============================================================================

def time_str_to_seconds(time_str: str) -> int:
    """
    Convert HH:MM:SS to seconds.
    
    Args:
        time_str: Time in format "HH:MM:SS"
        
    Returns:
        Total seconds as integer
    """
    if pd.isna(time_str):
        return 0
    
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
    except (ValueError, AttributeError):
        pass
    
    return 0

def seconds_to_time_str(seconds: int) -> str:
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def time_str_to_hours(time_str: str) -> float:
    """Convert HH:MM:SS to decimal hours."""
    return time_str_to_seconds(time_str) / 3600

def time_str_to_minutes(time_str: str) -> float:
    """Convert HH:MM:SS to minutes."""
    return time_str_to_seconds(time_str) / 60

# ============================================================================
# DATA EXTRACTION
# ============================================================================

def get_main_components(df: pd.DataFrame) -> List[str]:
    """
    Extract unique main components from dataframe.
    
    Returns:
        Sorted list of component names
    """
    if df is None or df.empty:
        return []
    
    return sorted(df['Component'].dropna().unique().tolist())

def get_sub_components(df: pd.DataFrame, main_component: str) -> List[str]:
    """
    Extract sub-components for a specific main component.
    
    Args:
        df: Dataframe with component data
        main_component: Name of main component
        
    Returns:
        Sorted list of sub-component names
    """
    if df is None or df.empty:
        return []
    
    filtered = df[df['Component'] == main_component]
    return sorted(filtered['Component.1'].dropna().unique().tolist())

def get_component_count(df: pd.DataFrame) -> int:
    """Get total number of sub-components."""
    return len(df) if df is not None else 0

# ============================================================================
# DATA FILTERING
# ============================================================================

def filter_by_main_component(df: pd.DataFrame, main_component: str) -> pd.DataFrame:
    """Filter data by main component."""
    if df is None or main_component is None:
        return None
    
    return df[df['Component'] == main_component].copy()

def filter_by_sub_components(df: pd.DataFrame, sub_components: List[str]) -> pd.DataFrame:
    """Filter data by one or more sub-components."""
    if df is None or not sub_components:
        return None
    
    return df[df['Component.1'].isin(sub_components)].copy()

def filter_data(df: pd.DataFrame, main_component: str, 
                sub_components: List[str]) -> Optional[pd.DataFrame]:
    """
    Filter dataframe by main and sub-components.
    
    Args:
        df: Original dataframe
        main_component: Main component to filter by
        sub_components: List of sub-components to include
        
    Returns:
        Filtered dataframe or None
    """
    if df is None:
        return None
    
    filtered = df[df['Component'] == main_component]
    
    if sub_components:
        filtered = filtered[filtered['Component.1'].isin(sub_components)]
    
    return filtered.copy()

# ============================================================================
# STATISTICS CALCULATION
# ============================================================================

def calculate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics from dataframe.
    
    Returns:
        Dictionary with calculated metrics
    """
    if df is None or df.empty:
        return {
            'total_sub_components': 0,
            'total_preparation_time': 0,
            'total_activity_time': 0,
            'total_time': 0,
            'avg_manpower': 0,
            'total_manpower': 0,
            'max_manpower': 0,
            'min_manpower': 0,
        }
    
    total_prep = sum(time_str_to_seconds(t) for t in df['Preparation/Finalization (h:mm:ss)'])
    total_activity = sum(time_str_to_seconds(t) for t in df['Activity (h:mm:ss)'])
    total_time = sum(time_str_to_seconds(t) for t in df['Total time (h:mm:ss)'])
    
    manpower_values = df['No of man power'].dropna()
    
    return {
        'total_sub_components': len(df),
        'total_preparation_time': total_prep,
        'total_activity_time': total_activity,
        'total_time': total_time,
        'avg_manpower': manpower_values.mean() if len(manpower_values) > 0 else 0,
        'total_manpower': int(manpower_values.sum()) if len(manpower_values) > 0 else 0,
        'max_manpower': int(manpower_values.max()) if len(manpower_values) > 0 else 0,
        'min_manpower': int(manpower_values.min()) if len(manpower_values) > 0 else 0,
    }

def calculate_component_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate summary statistics per component.
    
    Returns:
        Dataframe with component aggregates
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    summary = df.groupby('Component').agg({
        'Component.1': 'count',
        'No of man power': ['sum', 'mean', 'max'],
    }).round(2)
    
    return summary

# ============================================================================
# DATA TRANSFORMATION
# ============================================================================

def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add calculated columns to dataframe.
    
    Returns:
        Dataframe with new columns
    """
    df = df.copy()
    
    # Convert times to different units
    df['prep_time_hours'] = df['Preparation/Finalization (h:mm:ss)'].apply(time_str_to_hours)
    df['activity_time_hours'] = df['Activity (h:mm:ss)'].apply(time_str_to_hours)
    df['total_time_hours'] = df['Total time (h:mm:ss)'].apply(time_str_to_hours)
    
    # Calculate work-hours (person-hours)
    df['prep_work_hours'] = df['prep_time_hours'] * df['No of man power']
    df['activity_work_hours'] = df['activity_time_hours'] * df['No of man power']
    df['total_work_hours'] = df['total_time_hours'] * df['No of man power']
    
    return df

# ============================================================================
# DATA EXPORT
# ============================================================================

def prepare_export_csv(df: pd.DataFrame, filename: str = "export.csv") -> str:
    """
    Prepare CSV export of dataframe.
    
    Returns:
        CSV string content
    """
    if df is None or df.empty:
        return ""
    
    return df.to_csv(index=False)

def prepare_export_excel(df: pd.DataFrame, filename: str = "export.xlsx") -> bytes:
    """
    Prepare Excel export of dataframe.
    
    Returns:
        Excel file bytes
    """
    if df is None or df.empty:
        return b""
    
    # Note: Requires openpyxl
    output = pd.ExcelWriter(filename, engine='openpyxl')
    df.to_excel(output, sheet_name='Data', index=False)
    output.close()
    
    with open(filename, 'rb') as f:
        return f.read()

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def find_bottlenecks(df: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    """
    Identify sub-components with high time requirements.
    
    Args:
        df: Dataframe to analyze
        threshold: Time threshold in hours
        
    Returns:
        Dataframe with bottleneck components
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    df_copy = add_calculated_columns(df.copy())
    bottlenecks = df_copy[df_copy['total_time_hours'] > threshold]
    
    return bottlenecks.sort_values('total_time_hours', ascending=False)

def find_high_manpower_tasks(df: pd.DataFrame, threshold: int = 2) -> pd.DataFrame:
    """
    Identify tasks requiring high manpower.
    
    Args:
        df: Dataframe to analyze
        threshold: Manpower threshold
        
    Returns:
        Dataframe with high-manpower tasks
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    return df[df['No of man power'] >= threshold].sort_values(
        'No of man power',
        ascending=False
    )

def efficiency_analysis(df: pd.DataFrame) -> Dict:
    """
    Analyze efficiency metrics.
    
    Returns:
        Dictionary with efficiency metrics
    """
    if df is None or df.empty:
        return {}
    
    df_copy = add_calculated_columns(df.copy())
    
    return {
        'avg_time_per_component': df_copy['total_time_hours'].mean(),
        'avg_manpower_per_component': df_copy['No of man power'].mean(),
        'total_work_hours': df_copy['total_work_hours'].sum(),
        'efficiency_ratio': df_copy['total_time_hours'].sum() / df_copy['total_work_hours'].sum(),
    }

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_summary_report(df: pd.DataFrame, component_name: str = None) -> str:
    """
    Generate text summary report.
    
    Returns:
        Formatted report string
    """
    if df is None or df.empty:
        return "No data to generate report"
    
    stats = calculate_summary_stats(df)
    
    report = f"""
    ╔════════════════════════════════════════╗
    ║     COMPONENT SUMMARY REPORT           ║
    ╠════════════════════════════════════════╣
    """
    
    if component_name:
        report += f"║ Component: {component_name:<29}║\n"
    
    report += f"""║ Total Sub-Components: {stats['total_sub_components']:<18}║
    ║ Total Manpower: {stats['total_manpower']:<23}║
    ║ Avg Manpower: {stats['avg_manpower']:.1f:<25}║
    ║ Total Time: {seconds_to_time_str(int(stats['total_time'])):<26}║
    ╚════════════════════════════════════════╝
    """
    
    return report
