"""
Component Management & Visualization Tool
A Streamlit application for managing, filtering, and visualizing component data
with hierarchical structure (main component → sub-components)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Component Management Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced visuals
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary: #2E7D9E;
            --secondary: #F24236;
            --accent: #FDB833;
            --dark: #1A1A1A;
            --light: #F5F5F5;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Remove default padding */
        .main > div {
            padding-top: 1rem;
        }
        
        /* Custom card styling */
        .component-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #2E7D9E;
            transition: all 0.3s ease;
        }
        
        .component-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        /* Table styling */
        .dataframe {
            font-size: 0.9rem;
        }
        
        /* Metric boxes */
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'selected_main_component' not in st.session_state:
    st.session_state.selected_main_component = None
if 'selected_sub_components' not in st.session_state:
    st.session_state.selected_sub_components = []
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'upload_timestamp' not in st.session_state:
    st.session_state.upload_timestamp = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_excel_data(uploaded_file):
    """Load and parse Excel file with data validation."""
    try:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df
        st.session_state.upload_timestamp = datetime.now()
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def get_main_components(df):
    """Extract unique main components from dataframe."""
    if df is not None:
        return sorted(df['Component'].dropna().unique().tolist())
    return []

def get_sub_components(df, main_component):
    """Extract sub-components for a specific main component."""
    if df is not None:
        filtered = df[df['Component'] == main_component]
        return sorted(filtered['Component.1'].dropna().unique().tolist())
    return []

def filter_data(df, main_component, sub_components):
    """Filter dataframe by main and sub-components."""
    if df is None:
        return None
    
    filtered = df[df['Component'] == main_component]
    
    if sub_components:
        filtered = filtered[filtered['Component.1'].isin(sub_components)]
    
    return filtered

def calculate_summary_stats(df):
    """Calculate summary statistics from filtered data."""
    if df is None or df.empty:
        return {}
    
    stats = {
        'total_sub_components': len(df),
        'total_preparation_time': df['Preparation/Finalization (h:mm:ss)'].sum() if 'Preparation/Finalization (h:mm:ss)' in df.columns else 0,
        'total_activity_time': df['Activity (h:mm:ss)'].sum() if 'Activity (h:mm:ss)' in df.columns else 0,
        'total_time': df['Total time (h:mm:ss)'].sum() if 'Total time (h:mm:ss)' in df.columns else 0,
        'avg_manpower': df['No of man power'].mean() if 'No of man power' in df.columns else 0,
        'total_manpower': df['No of man power'].sum() if 'No of man power' in df.columns else 0,
    }
    return stats

def time_str_to_seconds(time_str):
    """Convert HH:MM:SS string to seconds."""
    if pd.isna(time_str):
        return 0
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        pass
    return 0

def seconds_to_time_str(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def export_filtered_data(df, filename="filtered_data.csv"):
    """Prepare filtered data for export."""
    return df.to_csv(index=False)

# ============================================================================
# SIDEBAR - DATA INPUT & CONTROLS
# ============================================================================

with st.sidebar:
    st.title("📋 Control Panel")
    st.markdown("---")
    
    # File upload section
    st.subheader("📁 Data Management")
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload your component data in Excel format"
    )
    
    if uploaded_file is not None:
        with st.spinner("Loading data..."):
            df = load_excel_data(uploaded_file)
            if df is not None:
                st.success(f"✅ File loaded successfully!")
                st.caption(f"Rows: {len(df)} | Last updated: {st.session_state.upload_timestamp.strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # View mode toggle
    st.subheader("👁️ View Options")
    view_mode = st.radio(
        "Select View",
        ["Component Selection", "Data Analysis", "Summary Report"],
        help="Switch between different views"
    )
    
    st.markdown("---")
    
    # Export options
    st.subheader("💾 Export Options")
    if st.session_state.data is not None and st.session_state.selected_sub_components:
        filtered_data = filter_data(
            st.session_state.data,
            st.session_state.selected_main_component,
            st.session_state.selected_sub_components
        )
        
        csv_data = export_filtered_data(filtered_data)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"component_{st.session_state.selected_main_component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

st.title("🔧 Component Management & Visualization")
st.markdown("Streamline maintenance timing and resource allocation")

if st.session_state.data is None:
    st.info("👈 Please upload an Excel file to get started")
    st.stop()

# ============================================================================
# VIEW 1: COMPONENT SELECTION
# ============================================================================

if view_mode == "Component Selection":
    st.header("Step 1: Select Main Component")
    
    main_components = get_main_components(st.session_state.data)
    
    # Create grid layout for component cards
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Available Components")
        
        # Component selection cards
        cols = st.columns(2)
        for idx, component in enumerate(main_components):
            with cols[idx % 2]:
                if st.button(
                    f"🔹 {component}",
                    key=f"comp_{component}",
                    use_container_width=True,
                    help=f"Click to select {component}"
                ):
                    st.session_state.selected_main_component = component
                    st.session_state.selected_sub_components = []
                    st.rerun()
    
    with col2:
        st.subheader("Selected")
        if st.session_state.selected_main_component:
            st.success(st.session_state.selected_main_component)
        else:
            st.info("None selected")
    
    st.markdown("---")
    
    # Sub-component selection
    if st.session_state.selected_main_component:
        st.header("Step 2: Select Sub-Components")
        
        sub_components = get_sub_components(
            st.session_state.data,
            st.session_state.selected_main_component
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Sub-components of {st.session_state.selected_main_component}")
            
            # Multi-select for sub-components
            selected = st.multiselect(
                "Choose sub-components (default: first one selected)",
                options=sub_components,
                default=sub_components[0:1] if sub_components else [],
                key="sub_comp_select"
            )
            
            st.session_state.selected_sub_components = selected
        
        with col2:
            st.subheader("Selected Count")
            st.metric("Sub-components", len(st.session_state.selected_sub_components))
        
        st.markdown("---")
        
        # Display selected data in table
        if st.session_state.selected_sub_components:
            st.header("Step 3: Preview Selected Data")
            
            filtered_df = filter_data(
                st.session_state.data,
                st.session_state.selected_main_component,
                st.session_state.selected_sub_components
            )
            
            st.subheader(f"Data for {st.session_state.selected_main_component}")
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Summary statistics
            stats = calculate_summary_stats(filtered_df)
            
            st.subheader("Summary Statistics")
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric("Total Sub-Components", stats['total_sub_components'])
            
            with metric_cols[1]:
                st.metric("Total Manpower", int(stats['total_manpower']))
            
            with metric_cols[2]:
                st.metric("Avg Manpower", f"{stats['avg_manpower']:.1f}")
            
            with metric_cols[3]:
                st.metric("Sub-components Selected", len(st.session_state.selected_sub_components))

# ============================================================================
# VIEW 2: DATA ANALYSIS
# ============================================================================

elif view_mode == "Data Analysis":
    st.header("Data Analysis & Insights")
    
    if st.session_state.selected_main_component and st.session_state.selected_sub_components:
        filtered_df = filter_data(
            st.session_state.data,
            st.session_state.selected_main_component,
            st.session_state.selected_sub_components
        )
        
        # Create visualization tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Table View", "Time Analysis", "Manpower Analysis", "Component Breakdown"])
        
        with tab1:
            st.subheader("Detailed Data View")
            st.dataframe(filtered_df, use_container_width=True)
        
        with tab2:
            st.subheader("Time Distribution Analysis")
            
            # Convert time columns to numeric for visualization
            try:
                prep_times = filtered_df['Preparation/Finalization (h:mm:ss)'].apply(time_str_to_seconds) / 3600
                activity_times = filtered_df['Activity (h:mm:ss)'].apply(time_str_to_seconds) / 3600
                
                fig = go.Figure(data=[
                    go.Bar(name='Preparation', x=filtered_df['Component.1'], y=prep_times),
                    go.Bar(name='Activity', x=filtered_df['Component.1'], y=activity_times)
                ])
                
                fig.update_layout(
                    barmode='stack',
                    title=f"Time Distribution for {st.session_state.selected_main_component}",
                    xaxis_title="Sub-Component",
                    yaxis_title="Time (Hours)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate time analysis: {str(e)}")
        
        with tab3:
            st.subheader("Manpower Requirements")
            
            try:
                fig = px.bar(
                    filtered_df,
                    x='Component.1',
                    y='No of man power',
                    title=f"Manpower Needed for {st.session_state.selected_main_component}",
                    labels={'Component.1': 'Sub-Component', 'No of man power': 'Number of People'}
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Manpower Required", int(filtered_df['No of man power'].sum()))
                with col2:
                    st.metric("Average Manpower", f"{filtered_df['No of man power'].mean():.1f}")
                with col3:
                    st.metric("Max Manpower", int(filtered_df['No of man power'].max()))
            except Exception as e:
                st.error(f"Could not generate manpower analysis: {str(e)}")
        
        with tab4:
            st.subheader("Component Breakdown")
            
            try:
                breakdown = filtered_df.groupby('Component.1').agg({
                    'Preparation/Finalization (h:mm:ss)': 'first',
                    'Activity (h:mm:ss)': 'first',
                    'Total time (h:mm:ss)': 'first',
                    'No of man power': 'first'
                }).reset_index()
                
                st.dataframe(breakdown, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate breakdown: {str(e)}")
    else:
        st.warning("Please select a component and sub-components first")

# ============================================================================
# VIEW 3: SUMMARY REPORT
# ============================================================================

elif view_mode == "Summary Report":
    st.header("Executive Summary Report")
    
    all_data = st.session_state.data
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Components", len(get_main_components(all_data)))
    
    with col2:
        st.metric("Total Sub-Components", len(all_data))
    
    with col3:
        st.metric("Total Manpower Required", int(all_data['No of man power'].sum()) if 'No of man power' in all_data.columns else 0)
    
    with col4:
        st.metric("Data Points", len(all_data))
    
    st.markdown("---")
    
    # Component overview
    st.subheader("Component Overview")
    
    component_summary = all_data.groupby('Component').agg({
        'Component.1': 'count',
        'No of man power': 'sum'
    }).rename(columns={'Component.1': 'Sub-Component Count'})
    
    st.dataframe(component_summary, use_container_width=True)
    
    # Visualization
    fig = px.bar(
        component_summary.reset_index(),
        x='Component',
        y='Sub-Component Count',
        title="Number of Sub-Components per Main Component",
        labels={'Sub-Component Count': 'Count'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🔧 Component Management Tool v1.0")

with col2:
    if st.session_state.upload_timestamp:
        st.caption(f"Last updated: {st.session_state.upload_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

with col3:
    st.caption("💡 Tip: Use sidebar to manage data and export results")
