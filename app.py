"""
KONE Component Maintenance Manager - FINAL FIXED VERSION
Works with ANY Excel structure - Dynamic column detection with fallback
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

st.markdown("""
    <style>
        .metric-box { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
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
# UTILITY FUNCTIONS
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
# COLUMN DETECTION - ROBUST VERSION
# ============================================================================

def find_column_by_keywords(df, keywords):
    """
    Find a column that contains any of the keywords.
    Keywords: list of strings to search for
    Returns: column name or None
    """
    col_names = df.columns.tolist()
    col_lower = [str(c).lower().strip() for c in col_names]
    
    for keyword in keywords:
        for i, col_lower_name in enumerate(col_lower):
            if keyword.lower() in col_lower_name:
                return col_names[i]
    return None

def detect_columns(df):
    """
    Automatically detect column names using keywords.
    Very robust - handles ANY variation of headers.
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
    
    # Find main component column
    columns_found['main'] = find_column_by_keywords(
        df, 
        ['module', 'main', 'category']
    )
    
    # Find sub component column
    columns_found['sub'] = find_column_by_keywords(
        df,
        ['sub', 'sub_module', 'submodule', 'group']
    )
    
    # Find component column (try multiple keywords)
    columns_found['component'] = find_column_by_keywords(
        df,
        ['component', 'item', 'name', 'equipment', 'device']
    )
    
    # Find prep time column
    columns_found['prep_time'] = find_column_by_keywords(
        df,
        ['prep', 'preparation', 'setup', 'finalization']
    )
    
    # Find activity time column
    columns_found['activity_time'] = find_column_by_keywords(
        df,
        ['activity', 'work', 'execution', 'action']
    )
    
    # Find total time column
    columns_found['total_time'] = find_column_by_keywords(
        df,
        ['total', 'total_time', 'duration']
    )
    
    # Find manpower column
    columns_found['manpower'] = find_column_by_keywords(
        df,
        ['man', 'power', 'personnel', 'people', 'workers', 'staff']
    )
    
    return columns_found

def load_excel(uploaded_file):
    """Load Excel file and detect columns"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Forward fill main and sub columns to handle NaN values
        cols_dict = detect_columns(df)
        
        if cols_dict['main'] and cols_dict['main'] in df.columns:
            df[cols_dict['main']] = df[cols_dict['main']].fillna(method='ffill')
        
        if cols_dict['sub'] and cols_dict['sub'] in df.columns:
            df[cols_dict['sub']] = df[cols_dict['sub']].fillna(method='ffill')
        
        st.session_state.data = df
        st.session_state.columns_dict = cols_dict
        st.session_state.upload_timestamp = datetime.now()
        
        return df, cols_dict
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        return None, {}

def get_main_values(df, col_dict):
    """Get unique main values - with error handling"""
    if df is None or col_dict.get('main') is None:
        return []
    
    try:
        col_name = col_dict['main']
        if col_name in df.columns:
            return sorted([str(x) for x in df[col_name].dropna().unique()])
    except Exception as e:
        st.error(f"Error getting main values: {str(e)}")
    
    return []

def get_sub_values(df, col_dict, main_value):
    """Get unique sub values - with error handling"""
    if df is None or col_dict.get('main') is None or col_dict.get('sub') is None:
        return []
    
    try:
        main_col = col_dict['main']
        sub_col = col_dict['sub']
        
        if main_col in df.columns and sub_col in df.columns:
            filtered = df[df[main_col].astype(str) == str(main_value)]
            return sorted([str(x) for x in filtered[sub_col].dropna().unique()])
    except Exception as e:
        st.error(f"Error getting sub values: {str(e)}")
    
    return []

def filter_data(df, col_dict, main_value, sub_values):
    """Filter data by selected values"""
    if df is None or col_dict.get('main') is None:
        return None
    
    try:
        main_col = col_dict['main']
        
        # Filter by main value
        filtered = df[df[main_col].astype(str) == str(main_value)].copy()
        
        # Filter by sub values if they exist
        if sub_values and col_dict.get('sub') and col_dict['sub'] in df.columns:
            sub_col = col_dict['sub']
            filtered = filtered[filtered[sub_col].astype(str).isin([str(v) for v in sub_values])]
        
        return filtered
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        return None

def calculate_stats(df, col_dict):
    """Calculate statistics safely"""
    if df is None or df.empty:
        return {}
    
    stats = {
        'records': len(df),
        'total_time': 0,
        'total_manpower': 0,
        'avg_manpower': 0,
    }
    
    try:
        if col_dict.get('total_time') and col_dict['total_time'] in df.columns:
            total_secs = sum(time_str_to_seconds(t) for t in df[col_dict['total_time']])
            stats['total_time'] = total_secs
    except:
        pass
    
    try:
        if col_dict.get('manpower') and col_dict['manpower'] in df.columns:
            manpower = pd.to_numeric(df[col_dict['manpower']], errors='coerce').dropna()
            if len(manpower) > 0:
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
    
    st.subheader("📁 Upload Excel Data")
    uploaded_file = st.file_uploader(
        "Choose your Excel file",
        type=['xlsx', 'xls'],
        help="Upload Excel with columns: Module, Sub Module, Component, Time, Manpower"
    )
    
    if uploaded_file is not None:
        with st.spinner("📥 Loading file..."):
            df, cols_dict = load_excel(uploaded_file)
            
            if df is not None:
                st.success(f"✅ Loaded {len(df)} records!")
                
                with st.expander("📋 Detected Columns"):
                    for key, val in cols_dict.items():
                        if val:
                            st.write(f"**{key.upper()}**: {val}")
                        else:
                            st.write(f"**{key.upper()}**: ❌ Not found")
            else:
                st.error("Failed to load file")
    
    st.markdown("---")
    
    st.subheader("👁️ View Mode")
    view_mode = st.radio(
        "Select View",
        ["🔍 Table View", "📊 Analytics", "📈 Summary"],
    )
    
    st.markdown("---")
    
    st.subheader("💾 Export")
    if (st.session_state.data is not None and 
        st.session_state.selected_sub and 
        st.session_state.columns_dict):
        
        filtered = filter_data(
            st.session_state.data,
            st.session_state.columns_dict,
            st.session_state.selected_main,
            st.session_state.selected_sub
        )
        
        if filtered is not None and len(filtered) > 0:
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

col_dict = st.session_state.columns_dict

# Check if columns were detected
if not col_dict.get('main'):
    st.error("❌ Could not detect main component column. Please check your Excel headers.")
    st.stop()

# ============================================================================
# VIEW 1: TABLE VIEW
# ============================================================================

if view_mode == "🔍 Table View":
    st.header("Data Selection & Preview")
    
    # Get main values
    main_values = get_main_values(st.session_state.data, col_dict)
    
    if not main_values:
        st.error("❌ No data found in main column")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📦 Select Main Category")
        for val in main_values[:10]:  # Show first 10
            if st.button(f"📦 {val}", key=f"main_{val}", use_container_width=True):
                st.session_state.selected_main = val
                st.session_state.selected_sub = []
                st.rerun()
    
    with col2:
        st.subheader("Selected")
        if st.session_state.selected_main:
            st.success(st.session_state.selected_main)
        else:
            st.info("None")
    
    st.markdown("---")
    
    # Sub-category selection
    if st.session_state.selected_main:
        if col_dict.get('sub'):
            sub_values = get_sub_values(st.session_state.data, col_dict, st.session_state.selected_main)
            
            if sub_values:
                st.subheader("🔹 Select Sub-Categories")
                selected_sub = st.multiselect(
                    "Choose items",
                    options=sub_values,
                    default=sub_values[0:1] if sub_values else [],
                    key="sub_select"
                )
                st.session_state.selected_sub = selected_sub
            else:
                st.warning("No sub-categories found")
        
        st.markdown("---")
        
        # Display filtered data
        if st.session_state.selected_sub:
            filtered_df = filter_data(
                st.session_state.data,
                col_dict,
                st.session_state.selected_main,
                st.session_state.selected_sub
            )
            
            if filtered_df is not None and len(filtered_df) > 0:
                st.subheader(f"📊 Data Preview ({len(filtered_df)} records)")
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Statistics
                stats = calculate_stats(filtered_df, col_dict)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Records", stats['records'])
                with col2:
                    time_str = seconds_to_time_str(int(stats['total_time'])) if stats['total_time'] > 0 else "N/A"
                    st.metric("Total Time", time_str)
                with col3:
                    st.metric("Total Manpower", int(stats['total_manpower']))
                with col4:
                    st.metric("Avg Manpower", f"{stats['avg_manpower']:.1f}")
            else:
                st.warning("No data found for selected filters")

# ============================================================================
# VIEW 2: ANALYTICS
# ============================================================================

elif view_mode == "📊 Analytics":
    
    if not st.session_state.selected_main or not st.session_state.selected_sub:
        st.warning("Please select a category and items first")
        st.stop()
    
    filtered_df = filter_data(
        st.session_state.data,
        col_dict,
        st.session_state.selected_main,
        st.session_state.selected_sub
    )
    
    if filtered_df is None or len(filtered_df) == 0:
        st.error("No data found")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["📋 Table", "⏱️ Time", "👥 Manpower"])
    
    with tab1:
        st.subheader("Complete Data")
        st.dataframe(filtered_df, use_container_width=True, height=500)
    
    with tab2:
        st.subheader("Time Analysis")
        if col_dict.get('prep_time') and col_dict.get('activity_time'):
            try:
                if (col_dict['prep_time'] in filtered_df.columns and 
                    col_dict['activity_time'] in filtered_df.columns):
                    
                    prep = filtered_df[col_dict['prep_time']].apply(time_str_to_hours)
                    activity = filtered_df[col_dict['activity_time']].apply(time_str_to_hours)
                    
                    component_col = col_dict.get('component', 'Item')
                    x_axis = filtered_df[component_col] if component_col in filtered_df.columns else range(len(filtered_df))
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Preparation', x=x_axis, y=prep),
                        go.Bar(name='Activity', x=x_axis, y=activity)
                    ])
                    
                    fig.update_layout(barmode='stack', height=500, hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate chart: {str(e)}")
        else:
            st.info("Time columns not found")
    
    with tab3:
        st.subheader("Manpower Requirements")
        if col_dict.get('manpower'):
            try:
                if col_dict['manpower'] in filtered_df.columns:
                    component_col = col_dict.get('component', 'Item')
                    x_axis = filtered_df[component_col] if component_col in filtered_df.columns else range(len(filtered_df))
                    
                    fig = px.bar(
                        x=x_axis,
                        y=filtered_df[col_dict['manpower']],
                        title="Manpower Needed",
                        color=filtered_df[col_dict['manpower']],
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
    
    main_values = get_main_values(st.session_state.data, col_dict)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Categories", len(main_values))
    with col2:
        st.metric("Total Records", len(st.session_state.data))
    with col3:
        if col_dict.get('manpower') and col_dict['manpower'] in st.session_state.data.columns:
            try:
                mp = pd.to_numeric(st.session_state.data[col_dict['manpower']], errors='coerce').dropna()
                st.metric("Total Manpower", int(mp.sum()))
            except:
                st.metric("Total Manpower", "N/A")
    with col4:
        if col_dict.get('total_time') and col_dict['total_time'] in st.session_state.data.columns:
            try:
                total_secs = sum(time_str_to_seconds(t) for t in st.session_state.data[col_dict['total_time']])
                st.metric("Total Time", seconds_to_time_str(int(total_secs)))
            except:
                st.metric("Total Time", "N/A")
    
    st.markdown("---")
    st.subheader("Category Summary")
    
    summary_data = []
    for main_val in main_values[:20]:  # Limit to 20
        try:
            category_df = st.session_state.data[
                st.session_state.data[col_dict['main']].astype(str) == str(main_val)
            ]
            
            summary_data.append({
                'Category': main_val,
                'Records': len(category_df),
                'Manpower': int(pd.to_numeric(category_df[col_dict['manpower']], errors='coerce').sum()) 
                           if col_dict.get('manpower') and col_dict['manpower'] in st.session_state.data.columns 
                           else 0
            })
        except:
            pass
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        try:
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
        except:
            pass

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 KONE Maintenance Manager v1.2")
with col2:
    if st.session_state.data is not None:
        st.caption(f"Loaded: {len(st.session_state.data)} records")
with col3:
    st.caption("✅ Upload any Excel file - Auto-detects structure!")
