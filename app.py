"""
KONE Component Maintenance Manager - OPTIMIZED FOR DYNAMIC EXCEL UPLOADS
Version: 1.1 - Production Ready for Streamlit Cloud

Key Features:
- Automatically detects column headers (no hard-coded names)
- Works with ANY Excel file with same header structure
- Upload different files anytime with same headers
- Dynamic filtering and analysis
- Perfect for varying maintenance data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="KONE Maintenance Manager",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
        .metric-box { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
        }
        .component-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #2E7D9E;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'columns_dict' not in st.session_state:
    st.session_state.columns_dict = {}
if 'selected_main' not in st.session_state:
    st.session_state.selected_main = None
if 'selected_sub' not in st.session_state:
    st.session_state.selected_sub = []

# ============================================================================
# UTILITY FUNCTIONS - TIME CONVERSION
# ============================================================================

def time_str_to_seconds(time_str):
    """Convert HH:MM:SS to seconds"""
    if pd.isna(time_str):
        return 0
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
    except:
        pass
    return 0

def seconds_to_time_str(seconds):
    """Convert seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def time_str_to_hours(time_str):
    """Convert HH:MM:SS to decimal hours"""
    return time_str_to_seconds(time_str) / 3600

# ============================================================================
# DATA LOADING & DETECTION
# ============================================================================

def detect_columns(df):
    """
    Automatically detect column mapping from Excel headers.
    Works with ANY Excel that has the same header structure.
    """
    columns_found = {
        'main': None,
        'sub': None,
        'component': None,
        'prep_time': None,
        'activity_time': None,
        'total_time': None,
        'manpower': None
    }
    
    # Get all column names
    col_names = df.columns.tolist()
    col_lower = [str(c).lower().strip() for c in col_names]
    
    # Detect Main Component column
    for col in col_lower:
        if 'module' in col and 'sub' not in col:
            columns_found['main'] = col_names[col_lower.index(col)]
            break
    
    # Detect Sub Component column
    for col in col_lower:
        if 'sub' in col and 'module' in col:
            columns_found['sub'] = col_names[col_lower.index(col)]
            break
    
    # Detect Component column
    for col in col_lower:
        if 'component' in col and 'sub' not in col:
            columns_found['component'] = col_names[col_lower.index(col)]
            break
    
    # Detect Time columns
    for col in col_lower:
        if 'preparation' in col or 'prep' in col:
            columns_found['prep_time'] = col_names[col_lower.index(col)]
        if 'activity' in col:
            columns_found['activity_time'] = col_names[col_lower.index(col)]
        if 'total' in col and 'time' in col:
            columns_found['total_time'] = col_names[col_lower.index(col)]
    
    # Detect Manpower column
    for col in col_lower:
        if 'man' in col or 'power' in col or 'personnel' in col:
            columns_found['manpower'] = col_names[col_lower.index(col)]
            break
    
    return columns_found

def load_excel(uploaded_file):
    """Load Excel and auto-detect columns"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Forward fill main and sub columns
        if len(df) > 0:
            # Find which columns are the main/sub
            cols_dict = detect_columns(df)
            
            if cols_dict['main']:
                df[cols_dict['main']] = df[cols_dict['main']].fillna(method='ffill')
            if cols_dict['sub']:
                df[cols_dict['sub']] = df[cols_dict['sub']].fillna(method='ffill')
        
        st.session_state.data = df
        st.session_state.columns_dict = detect_columns(df)
        st.session_state.upload_timestamp = datetime.now()
        return df, detect_columns(df)
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None, {}

def get_main_values(df, col):
    """Get unique main values"""
    if df is None or col is None:
        return []
    return sorted(df[col].dropna().unique().tolist())

def get_sub_values(df, main_col, main_val, sub_col):
    """Get unique sub values for a main value"""
    if df is None or main_col is None or sub_col is None:
        return []
    filtered = df[df[main_col] == main_val]
    return sorted(filtered[sub_col].dropna().unique().tolist())

def filter_data(df, main_col, main_val, sub_col, sub_vals):
    """Filter data dynamically"""
    if df is None or main_col is None:
        return None
    
    filtered = df[df[main_col] == main_val]
    
    if sub_col and sub_vals:
        filtered = filtered[filtered[sub_col].isin(sub_vals)]
    
    return filtered

def calculate_stats(df, cols_dict):
    """Calculate statistics from any Excel structure"""
    if df is None or df.empty:
        return {}
    
    stats = {
        'records': len(df),
        'total_time': 0,
        'total_manpower': 0,
    }
    
    # Calculate time if column exists
    if cols_dict.get('total_time') and cols_dict['total_time'] in df.columns:
        try:
            total_secs = sum(time_str_to_seconds(t) for t in df[cols_dict['total_time']])
            stats['total_time'] = total_secs
        except:
            pass
    
    # Calculate manpower if column exists
    if cols_dict.get('manpower') and cols_dict['manpower'] in df.columns:
        try:
            manpower = df[cols_dict['manpower']].dropna()
            stats['total_manpower'] = int(manpower.sum())
            stats['avg_manpower'] = manpower.mean()
        except:
            pass
    
    return stats

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🔧 Control Panel")
    st.markdown("---")
    
    # File upload - DYNAMIC EXCEL SUPPORT
    st.subheader("📁 Upload Excel Data")
    uploaded_file = st.file_uploader(
        "Upload your Excel file",
        type=['xlsx', 'xls'],
        help="Upload any Excel file with same column structure"
    )
    
    if uploaded_file is not None:
        with st.spinner("Loading and analyzing..."):
            df, cols_dict = load_excel(uploaded_file)
            if df is not None:
                st.success(f"✅ Loaded {len(df)} records!")
                
                # Show detected columns
                with st.expander("📋 Detected Columns"):
                    for key, val in cols_dict.items():
                        if val:
                            st.caption(f"**{key.upper()}**: {val}")
    
    st.markdown("---")
    
    # View selection
    st.subheader("👁️ View Mode")
    view_mode = st.radio(
        "Select View",
        ["🔍 Table View", "📊 Analytics", "📈 Summary"],
    )
    
    st.markdown("---")
    
    # Export
    st.subheader("💾 Export")
    if st.session_state.data is not None and st.session_state.selected_sub:
        filtered = filter_data(
            st.session_state.data,
            st.session_state.columns_dict['main'],
            st.session_state.selected_main,
            st.session_state.columns_dict['sub'],
            st.session_state.selected_sub
        )
        
        csv = filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🔧 KONE Maintenance Component Manager")
st.markdown("Upload Excel → Select Data → Analyze → Export")

if st.session_state.data is None:
    st.info("👈 Upload your Excel file in the sidebar to get started")
    st.stop()

cols_dict = st.session_state.columns_dict

# ============================================================================
# VIEW 1: TABLE VIEW (DEFAULT)
# ============================================================================

if view_mode == "🔍 Table View":
    
    st.header("Data Selection & Preview")
    
    if cols_dict.get('main'):
        # Select main category
        main_values = get_main_values(st.session_state.data, cols_dict['main'])
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📦 Select Main Category")
            for val in main_values:
                if st.button(f"📦 {val}", key=f"main_{val}", use_container_width=True):
                    st.session_state.selected_main = val
                    st.session_state.selected_sub = []
                    st.rerun()
        
        with col2:
            st.subheader("Selected")
            if st.session_state.selected_main:
                st.success(st.session_state.selected_main)
        
        st.markdown("---")
        
        # Select sub categories
        if st.session_state.selected_main:
            sub_values = get_sub_values(
                st.session_state.data,
                cols_dict['main'],
                st.session_state.selected_main,
                cols_dict['sub']
            )
            
            st.subheader("🔹 Select Sub-Categories")
            selected_sub = st.multiselect(
                "Choose items",
                options=sub_values,
                default=sub_values[0:1] if sub_values else [],
                key="sub_select"
            )
            st.session_state.selected_sub = selected_sub
            
            st.markdown("---")
            
            # Display filtered data
            if st.session_state.selected_sub:
                filtered_df = filter_data(
                    st.session_state.data,
                    cols_dict['main'],
                    st.session_state.selected_main,
                    cols_dict['sub'],
                    st.session_state.selected_sub
                )
                
                st.subheader(f"📊 Data Preview ({len(filtered_df)} records)")
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Statistics
                stats = calculate_stats(filtered_df, cols_dict)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Records", stats['records'])
                with col2:
                    st.metric("Total Time", seconds_to_time_str(int(stats['total_time'])) if stats['total_time'] > 0 else "N/A")
                with col3:
                    st.metric("Total Manpower", int(stats['total_manpower']))
                with col4:
                    st.metric("Avg Manpower", f"{stats.get('avg_manpower', 0):.1f}")

# ============================================================================
# VIEW 2: ANALYTICS
# ============================================================================

elif view_mode == "📊 Analytics":
    
    if not st.session_state.selected_main or not st.session_state.selected_sub:
        st.warning("Please select a category and items first")
        st.stop()
    
    filtered_df = filter_data(
        st.session_state.data,
        cols_dict['main'],
        st.session_state.selected_main,
        cols_dict['sub'],
        st.session_state.selected_sub
    )
    
    tab1, tab2, tab3 = st.tabs(["📋 Table", "⏱️ Time", "👥 Manpower"])
    
    with tab1:
        st.subheader("Complete Data")
        st.dataframe(filtered_df, use_container_width=True, height=500)
    
    with tab2:
        st.subheader("Time Analysis")
        if cols_dict.get('prep_time') and cols_dict.get('activity_time'):
            try:
                prep = filtered_df[cols_dict['prep_time']].apply(time_str_to_hours)
                activity = filtered_df[cols_dict['activity_time']].apply(time_str_to_hours)
                
                component_col = cols_dict.get('component', 'Item')
                
                fig = go.Figure(data=[
                    go.Bar(name='Preparation', x=filtered_df[component_col], y=prep),
                    go.Bar(name='Activity', x=filtered_df[component_col], y=activity)
                ])
                
                fig.update_layout(barmode='stack', height=500, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate chart: {str(e)}")
    
    with tab3:
        st.subheader("Manpower Requirements")
        if cols_dict.get('manpower'):
            try:
                component_col = cols_dict.get('component', 'Item')
                fig = px.bar(
                    filtered_df,
                    x=component_col,
                    y=cols_dict['manpower'],
                    title="Manpower Needed",
                    color=cols_dict['manpower'],
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate chart: {str(e)}")

# ============================================================================
# VIEW 3: SUMMARY
# ============================================================================

elif view_mode == "📈 Summary":
    
    st.header("Summary Report")
    
    if cols_dict.get('main'):
        main_values = get_main_values(st.session_state.data, cols_dict['main'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Categories", len(main_values))
        with col2:
            st.metric("Total Records", len(st.session_state.data))
        with col3:
            if cols_dict.get('manpower'):
                st.metric("Total Manpower", int(st.session_state.data[cols_dict['manpower']].sum()))
        with col4:
            if cols_dict.get('total_time'):
                total_secs = sum(time_str_to_seconds(t) for t in st.session_state.data[cols_dict['total_time']])
                st.metric("Total Time", seconds_to_time_str(int(total_secs)))
        
        st.markdown("---")
        st.subheader("Category Breakdown")
        
        # Summary by main category
        summary_data = []
        for main_val in main_values:
            category_df = st.session_state.data[st.session_state.data[cols_dict['main']] == main_val]
            summary_data.append({
                'Category': main_val,
                'Records': len(category_df),
                'Manpower': int(category_df[cols_dict['manpower']].sum()) if cols_dict.get('manpower') else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Chart
        if len(summary_df) > 0:
            fig = px.bar(
                summary_df,
                x='Category',
                y='Records',
                title='Records per Category',
                color='Manpower',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 KONE Maintenance Manager v1.1")
with col2:
    if st.session_state.data is not None:
        st.caption(f"Loaded: {len(st.session_state.data)} records")
with col3:
    st.caption("💡 Upload any Excel file with same headers")
