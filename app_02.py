import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(page_title="Data Science Jobs Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    h1 {
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    h2 {
        color: #1f77b4;
        font-size: 1.8em;
        margin-top: 30px;
    }
    .metric-card {
        background-color: #f0f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📊 Data Science Jobs Dashboard")
st.markdown("Explore and analyze Data Science job postings with interactive visualizations")

# Load data with error handling
@st.cache_data
def load_data(file_path):
    """Load CSV file with error handling"""
    try:
        if not os.path.exists(file_path):
            st.error(f"❌ File not found: {file_path}")
            st.info("Please ensure the DataScientist.csv file is in the same directory as this app.")
            return None
        
        df = pd.read_csv(file_path, index_col=0)
        return df
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        return None

# Load the dataset
FILE_PATH = "DataScientist.csv"
df = load_data(FILE_PATH)

if df is not None:
    # Data preprocessing
    # Clean salary columns by extracting numeric values
    df['Salary_Min'] = df['Salary Estimate'].str.extract('(\d+)').astype(float) * 1000
    df['Salary_Max'] = df['Salary Estimate'].str.extract(r'\$(\d+)K-\$(\d+)K').iloc[:, 1].astype(float) * 1000
    df['Avg_Salary'] = (df['Salary_Min'] + df['Salary_Max']) / 2
    
    # Drop rows with missing critical data
    df_clean = df.dropna(subset=['Job Title', 'Sector', 'Rating'])
    
    # ==================== SIDEBAR FILTERS ====================
    st.sidebar.markdown("## 🔍 Filters")
    
    # Sector filter
    sectors = sorted(df_clean['Sector'].dropna().unique())
    selected_sectors = st.sidebar.multiselect(
        "Select Sector(s)",
        options=sectors,
        default=sectors[:3] if len(sectors) > 3 else sectors
    )
    
    # Company size filter
    sizes = sorted(df_clean['Size'].dropna().unique())
    selected_sizes = st.sidebar.multiselect(
        "Select Company Size(s)",
        options=sizes,
        default=sizes if len(sizes) <= 3 else sizes[:3]
    )
    
    # Rating range filter
    min_rating = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=3.0, step=0.5)
    
    # Apply filters
    filtered_df = df_clean[
        (df_clean['Sector'].isin(selected_sectors)) &
        (df_clean['Size'].isin(selected_sizes)) &
        (df_clean['Rating'] >= min_rating)
    ]
    
    # Display filter info
    st.sidebar.markdown(f"### 📈 Summary")
    st.sidebar.metric("Total Jobs Found", len(filtered_df))
    st.sidebar.metric("Avg Rating", f"{filtered_df['Rating'].mean():.2f}")
    st.sidebar.metric("Avg Salary", f"${filtered_df['Avg_Salary'].mean():,.0f}")
    
    # ==================== MAIN DASHBOARD ====================
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Positions", len(filtered_df))
    with col2:
        st.metric("Avg Salary (K)", f"${filtered_df['Avg_Salary'].mean() / 1000:.0f}K")
    with col3:
        st.metric("Avg Rating", f"{filtered_df['Rating'].mean():.2f} ⭐")
    with col4:
        st.metric("Unique Companies", filtered_df['Company Name'].nunique())
    
    st.markdown("---")
    
    # ==================== CHARTS SECTION ====================
    st.markdown("## 📊 Interactive Visualizations")
    
    chart_col1, chart_col2 = st.columns(2)
    
    # Chart 1: Bar Chart - Top Job Titles
    with chart_col1:
        st.markdown("### 1️⃣ Top 10 Job Titles")
        job_counts = filtered_df['Job Title'].value_counts().head(10).reset_index()
        job_counts.columns = ['Job Title', 'Count']
        fig_bar = px.bar(
            job_counts,
            y='Job Title',
            x='Count',
            orientation='h',
            labels={'Count': 'Number of Positions'},
            color='Count',
            color_continuous_scale='Blues',
            height=400
        )
        fig_bar.update_layout(
            showlegend=False,
            hovermode='y unified',
            margin=dict(l=150, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Chart 2: Pie Chart - Jobs by Sector
    with chart_col2:
        st.markdown("### 2️⃣ Job Distribution by Sector")
        sector_counts = filtered_df['Sector'].value_counts().head(8)
        fig_pie = px.pie(
            names=sector_counts.index,
            values=sector_counts.values,
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Chart 3: Line Chart - Average Salary by Company Size
    st.markdown("### 3️⃣ Average Salary Trend by Company Size")
    
    size_salary = filtered_df.groupby('Size')['Avg_Salary'].mean().sort_values(ascending=False)
    
    if len(size_salary) > 0:
        fig_line = px.line(
            x=size_salary.index,
            y=size_salary.values,
            markers=True,
            labels={'x': 'Company Size', 'y': 'Average Salary ($)'},
            title='Salary Trend Across Company Sizes',
            color_discrete_sequence=['#1f77b4'],
            height=400
        )
        fig_line.update_traces(
            line=dict(width=3),
            marker=dict(size=10)
        )
        fig_line.update_layout(
            hovermode='x unified',
            margin=dict(l=50, r=20, t=60, b=50)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("⚠️ Not enough data to display salary trends")
    
    st.markdown("---")
    
    # ==================== RAW DATA TABLE ====================
    st.markdown("## 📋 Raw Data Table")
    
    # Select columns to display
    display_columns = [
        'Job Title', 'Company Name', 'Location', 'Salary Estimate', 
        'Rating', 'Sector', 'Size', 'Revenue'
    ]
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📊 Showing {len(filtered_df)} jobs")
    with col2:
        csv = filtered_df[available_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="data_science_jobs.csv",
            mime="text/csv"
        )
    with col3:
        st.info(f"📌 Total Records in Dataset: {len(df)}")
    
    # Display the table with pagination
    page_size = st.slider("Rows per page", 5, 50, 10)
    total_pages = (len(filtered_df) // page_size) + (1 if len(filtered_df) % page_size != 0 else 0)
    
    if total_pages > 0:
        page_number = st.selectbox("Select Page", range(1, total_pages + 1))
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        
        # Display table
        st.dataframe(
            filtered_df[available_columns].iloc[start_idx:end_idx].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        st.markdown(f"*Page {page_number} of {total_pages}*")
    
    st.markdown("---")
    st.markdown("**Dashboard Created with Streamlit & Plotly** | Last Updated: 2026")

else:
    st.error("🚫 Unable to load the dashboard. Please check if the DataScientist.csv file exists.")