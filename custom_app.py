"""
KONE Component Management Tool - CUSTOMIZED FOR YOUR DATA
Optimized for your Excel structure: Module > Sub Module > Components
With 93 rows of maintenance data
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
    page_title="KONE Component Maintenance Manager",
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
            transition: all 0.3s ease;
        }
        .component-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = None
if 'selected_sub_modules' not in st.session_state:
    st.session_state.selected_sub_modules = []
if 'upload_timestamp' not in st.session_state:
    st.session_state.upload_timestamp = None

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
# DATA LOADING & CLEANING
# ============================================================================

def load_and_clean_data(uploaded_file):
    """Load Excel and clean the Module/Sub Module hierarchy"""
    df = pd.read_excel(uploaded_file)
    
    # Forward fill Module and Sub Module to handle NaN values
    df['Module'] = df['Module'].fillna(method='ffill')
    df['Sub Module'] = df['Sub Module'].fillna(method='ffill')
    
    st.session_state.data = df
    st.session_state.upload_timestamp = datetime.now()
    return df

def get_modules(df):
    """Get unique modules"""
    if df is None:
        return []
    return sorted(df['Module'].dropna().unique().tolist())

def get_sub_modules(df, module):
    """Get sub-modules for a specific module"""
    if df is None or module is None:
        return []
    filtered = df[df['Module'] == module]
    return sorted(filtered['Sub Module'].dropna().unique().tolist())

def get_components(df, module, sub_modules):
    """Get components for selected module and sub-modules"""
    if df is None or module is None:
        return None
    
    filtered = df[df['Module'] == module]
    
    if sub_modules:
        filtered = filtered[filtered['Sub Module'].isin(sub_modules)]
    
    return filtered

# ============================================================================
# STATISTICS & CALCULATIONS
# ============================================================================

def calculate_stats(df):
    """Calculate summary statistics"""
    if df is None or df.empty:
        return {}
    
    prep_col = 'Preparation/Finalization (h:mm:ss)'
    activity_col = 'Activity \n(h:mm:ss)'
    total_col = 'Total time \n(h:mm:ss)'
    
    total_prep = sum(time_str_to_seconds(t) for t in df[prep_col])
    total_activity = sum(time_str_to_seconds(t) for t in df[activity_col])
    total_time = sum(time_str_to_seconds(t) for t in df[total_col])
    
    manpower = df['No of man power'].dropna()
    
    return {
        'components': len(df),
        'prep_time': total_prep,
        'activity_time': total_activity,
        'total_time': total_time,
        'avg_manpower': manpower.mean() if len(manpower) > 0 else 0,
        'total_manpower': int(manpower.sum()) if len(manpower) > 0 else 0,
    }

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🔧 Control Panel")
    st.markdown("---")
    
    # File upload
    st.subheader("📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload your KONE maintenance data"
    )
    
    if uploaded_file is not None:
        with st.spinner("Loading data..."):
            df = load_and_clean_data(uploaded_file)
            st.success(f"✅ Loaded {len(df)} maintenance records!")
            st.caption(f"Last updated: {st.session_state.upload_timestamp.strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # View selection
    st.subheader("👁️ View Mode")
    view_mode = st.radio(
        "Select View",
        ["🔍 Component Selection", "📊 Analytics", "📈 Summary Report"],
        help="Switch between different analysis views"
    )
    
    st.markdown("---")
    
    # Export
    st.subheader("💾 Export")
    if st.session_state.data is not None and st.session_state.selected_sub_modules:
        filtered_df = get_components(
            st.session_state.data,
            st.session_state.selected_module,
            st.session_state.selected_sub_modules
        )
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"maintenance_{st.session_state.selected_module}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ============================================================================
# MAIN TITLE
# ============================================================================

st.title("🔧 KONE Maintenance Component Manager")
st.markdown("### Optimize maintenance timing and resource allocation")

if st.session_state.data is None:
    st.warning("👈 Upload your Excel file to get started")
    st.stop()

# ============================================================================
# VIEW 1: COMPONENT SELECTION
# ============================================================================

if view_mode == "🔍 Component Selection":
    st.header("Step 1: Select Module")
    
    modules = get_modules(st.session_state.data)
    
    cols = st.columns(3)
    for idx, module in enumerate(modules):
        with cols[idx % 3]:
            if st.button(f"📦 {module}", key=f"mod_{module}", use_container_width=True):
                st.session_state.selected_module = module
                st.session_state.selected_sub_modules = []
                st.rerun()
    
    if st.session_state.selected_module:
        st.markdown(f"**✅ Selected Module:** {st.session_state.selected_module}")
        st.markdown("---")
        
        st.header("Step 2: Select Sub-Modules")
        sub_modules = get_sub_modules(st.session_state.data, st.session_state.selected_module)
        
        selected = st.multiselect(
            "Choose sub-modules",
            options=sub_modules,
            default=sub_modules[0:1] if sub_modules else [],
            key="sub_mod_select"
        )
        
        st.session_state.selected_sub_modules = selected
        
        if st.session_state.selected_sub_modules:
            st.markdown("---")
            st.header("Step 3: Component Details")
            
            filtered_df = get_components(
                st.session_state.data,
                st.session_state.selected_module,
                st.session_state.selected_sub_modules
            )
            
            # Display data
            display_cols = [
                'Module', 'Sub Module', 'Components',
                'Preparation/Finalization (h:mm:ss)', 'Activity \n(h:mm:ss)',
                'Total time \n(h:mm:ss)', 'No of man power'
            ]
            
            st.subheader(f"Components: {len(filtered_df)} items")
            st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
            
            # Statistics
            stats = calculate_stats(filtered_df)
            
            st.markdown("---")
            st.subheader("📊 Summary Statistics")
            
            stat_cols = st.columns(4)
            with stat_cols[0]:
                st.metric("Total Components", stats['components'])
            with stat_cols[1]:
                st.metric("Total Manpower", stats['total_manpower'])
            with stat_cols[2]:
                st.metric("Avg Manpower", f"{stats['avg_manpower']:.1f}")
            with stat_cols[3]:
                st.metric("Total Time", seconds_to_time_str(int(stats['total_time'])))

# ============================================================================
# VIEW 2: ANALYTICS
# ============================================================================

elif view_mode == "📊 Analytics":
    
    if not st.session_state.selected_module or not st.session_state.selected_sub_modules:
        st.warning("Please select a module and sub-modules first")
        st.stop()
    
    filtered_df = get_components(
        st.session_state.data,
        st.session_state.selected_module,
        st.session_state.selected_sub_modules
    )
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Table", "⏱️ Time", "👥 Manpower", "📉 Analysis"])
    
    with tab1:
        st.subheader("Detailed Component Data")
        st.dataframe(filtered_df, use_container_width=True, height=500)
    
    with tab2:
        st.subheader("Time Distribution Analysis")
        
        try:
            prep_times = filtered_df['Preparation/Finalization (h:mm:ss)'].apply(time_str_to_hours)
            activity_times = filtered_df['Activity \n(h:mm:ss)'].apply(time_str_to_hours)
            
            fig = go.Figure(data=[
                go.Bar(name='Preparation', x=filtered_df['Components'], y=prep_times),
                go.Bar(name='Activity', x=filtered_df['Components'], y=activity_times)
            ])
            
            fig.update_layout(
                barmode='stack',
                title=f"Time Breakdown for {st.session_state.selected_module}",
                xaxis_title="Component",
                yaxis_title="Time (Hours)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not generate chart: {str(e)}")
    
    with tab3:
        st.subheader("Manpower Requirements")
        
        try:
            fig = px.bar(
                filtered_df,
                x='Components',
                y='No of man power',
                title=f"Manpower Needed",
                labels={'Components': 'Component', 'No of man power': 'Number of People'},
                color='No of man power',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Manpower", int(filtered_df['No of man power'].sum()))
            with col2:
                st.metric("Average Manpower", f"{filtered_df['No of man power'].mean():.1f}")
            with col3:
                st.metric("Max Manpower", int(filtered_df['No of man power'].max()))
        except Exception as e:
            st.error(f"Could not generate chart: {str(e)}")
    
    with tab4:
        st.subheader("Component Efficiency Analysis")
        
        try:
            analysis_df = filtered_df[[
                'Components', 
                'Preparation/Finalization (h:mm:ss)',
                'Activity \n(h:mm:ss)',
                'Total time \n(h:mm:ss)',
                'No of man power'
            ]].copy()
            
            # Convert time to hours for efficiency calculation
            analysis_df['Prep Hours'] = analysis_df['Preparation/Finalization (h:mm:ss)'].apply(time_str_to_hours)
            analysis_df['Activity Hours'] = analysis_df['Activity \n(h:mm:ss)'].apply(time_str_to_hours)
            analysis_df['Total Hours'] = analysis_df['Total time \n(h:mm:ss)'].apply(time_str_to_hours)
            analysis_df['Work Hours'] = analysis_df['Total Hours'] * analysis_df['No of man power']
            
            st.dataframe(analysis_df, use_container_width=True)
            
            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Time per Component (Hours)", f"{analysis_df['Total Hours'].mean():.2f}")
            with col2:
                st.metric("Total Work Hours", f"{analysis_df['Work Hours'].sum():.1f}")
            with col3:
                st.metric("Efficiency Ratio", f"{(analysis_df['Total Hours'].sum() / analysis_df['Work Hours'].sum()):.2%}")
            with col4:
                st.metric("Avg Work Hours per Unit", f"{analysis_df['Work Hours'].mean():.1f}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============================================================================
# VIEW 3: SUMMARY REPORT
# ============================================================================

elif view_mode == "📈 Summary Report":
    
    st.header("Overall Summary Report")
    
    all_data = st.session_state.data
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Modules", len(get_modules(all_data)))
    with col2:
        st.metric("Total Components", len(all_data))
    with col3:
        st.metric("Total Manpower Required", int(all_data['No of man power'].sum()))
    with col4:
        total_secs = sum(time_str_to_seconds(t) for t in all_data['Total time \n(h:mm:ss)'])
        st.metric("Total Maintenance Time", seconds_to_time_str(int(total_secs)))
    
    st.markdown("---")
    
    # Module breakdown
    st.subheader("Module Breakdown")
    
    module_summary = all_data.groupby('Module').agg({
        'Components': 'count',
        'No of man power': 'sum'
    }).rename(columns={'Components': 'Total Components'})
    
    st.dataframe(module_summary, use_container_width=True)
    
    # Visualization
    fig = px.bar(
        module_summary.reset_index(),
        x='Module',
        y='Total Components',
        title="Components per Module",
        labels={'Total Components': 'Number of Components'},
        color='No of man power',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Time analysis
    st.markdown("---")
    st.subheader("Time Analysis by Module")
    
    try:
        time_analysis = []
        for module in get_modules(all_data):
            module_data = all_data[all_data['Module'] == module]
            total_secs = sum(time_str_to_seconds(t) for t in module_data['Total time \n(h:mm:ss)'])
            time_analysis.append({
                'Module': module,
                'Total Time (Hours)': total_secs / 3600,
                'Components': len(module_data)
            })
        
        time_df = pd.DataFrame(time_analysis)
        
        fig = px.bar(
            time_df,
            x='Module',
            y='Total Time (Hours)',
            title="Total Maintenance Time Required by Module",
            color='Components',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate time analysis: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 KONE Maintenance Manager v1.0")
with col2:
    if st.session_state.upload_timestamp:
        st.caption(f"Data updated: {st.session_state.upload_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
with col3:
    st.caption("💡 Select a module to analyze component data")
