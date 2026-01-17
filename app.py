import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page Config
st.set_page_config(
    page_title="Team Performance Dashboard", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    
    .sub-header {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-top: -10px;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(145deg, #1e1e2f 0%, #2d2d44 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
    }
    
    .delta-positive {
        background: rgba(72, 187, 120, 0.2);
        color: #48bb78;
    }
    
    .delta-negative {
        background: rgba(245, 101, 101, 0.2);
        color: #f56565;
    }
    
    .delta-neutral {
        background: rgba(160, 174, 192, 0.2);
        color: #a0aec0;
    }
    
    /* Section Headers */
    .section-header {
        color: #e2e8f0;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 20px;
    }
    
    /* Leaderboard */
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        margin: 8px 0;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .leaderboard-item:hover {
        background: rgba(255,255,255,0.06);
        transform: translateX(4px);
    }
    
    .rank-1 { border-left-color: #ffd700; }
    .rank-2 { border-left-color: #c0c0c0; }
    .rank-3 { border-left-color: #cd7f32; }
    .rank-other { border-left-color: #667eea; }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a0aec0;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
    }
    
    /* Data table */
    .dataframe {
        background: rgba(255,255,255,0.02) !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(path):
    """Load and preprocess Jira data"""
    import os
    paths_to_try = [path, "Jira.csv", "../Jira.csv"]
    
    for p in paths_to_try:
        if os.path.exists(p):
            path = p
            break
    else:
        st.error("❌ Jira.csv not found!")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    
    # Parse dates
    date_cols = ['Created', 'Updated', 'Resolved']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%d/%b/%y %I:%M %p', errors='coerce')
    
    # Clean data
    df['Assignee'] = df['Assignee'].fillna('Unassigned')
    df['Status'] = df['Status'].fillna('Unknown')
    df['Priority'] = df['Priority'].fillna('Medium')
    df['Issue Type'] = df['Issue Type'].fillna('Task')
    df['Reporter'] = df['Reporter'].fillna('Unknown')
    
    # Calculate resolution time (in days)
    if 'Created' in df.columns and 'Resolved' in df.columns:
        df['Resolution Days'] = (df['Resolved'] - df['Created']).dt.days
    
    # Extract week for trend analysis
    if 'Created' in df.columns:
        df['Created Week'] = df['Created'].dt.isocalendar().week
        df['Created Month'] = df['Created'].dt.month_name()
    
    return df


def create_metric_card(label, value, delta=None, delta_type="neutral"):
    """Create a styled metric card"""
    delta_class = f"delta-{delta_type}"
    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """


def render_leaderboard(df, done_statuses):
    """Render team leaderboard"""
    leaderboard = df.groupby('Assignee').agg({
        'Issue key': 'count',
        'Status': lambda x: (x.isin(done_statuses)).sum()
    }).reset_index()
    leaderboard.columns = ['Assignee', 'Total', 'Completed']
    leaderboard['Efficiency'] = (leaderboard['Completed'] / leaderboard['Total'] * 100).round(1)
    leaderboard = leaderboard.sort_values('Completed', ascending=False)
    
    st.markdown("### 🏆 Team Leaderboard")
    
    for idx, row in leaderboard.head(5).iterrows():
        rank = leaderboard.index.get_loc(idx) + 1
        rank_class = f"rank-{rank}" if rank <= 3 else "rank-other"
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        
        st.markdown(f"""
        <div class="leaderboard-item {rank_class}">
            <span style="font-size: 1.5rem; margin-right: 16px;">{medal}</span>
            <div style="flex-grow: 1;">
                <div style="color: #e2e8f0; font-weight: 500;">{row['Assignee']}</div>
                <div style="color: #a0aec0; font-size: 0.85rem;">{row['Completed']}/{row['Total']} completed • {row['Efficiency']}% efficiency</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Team Leads Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time performance analytics & insights for your team</p>', unsafe_allow_html=True)
    
    # Load Data
    df = load_data("../Jira.csv")
    
    if df.empty:
        st.error("No data available. Please check your Jira.csv file.")
        return
    
    # Status categories
    done_statuses = ['Done', 'Resolved', 'Closed', 'Completed']
    in_progress_statuses = ['In Progress', 'In Review']
    todo_statuses = ['To Do', 'Idea', 'Open']
    
    # Sidebar Filters
    with st.sidebar:
        st.markdown("## 🎛️ Filters")
        st.markdown("---")
        
        # Team member filter
        assignees = sorted(df['Assignee'].unique().tolist())
        selected_assignees = st.multiselect(
            "👥 Team Members",
            assignees,
            default=assignees,
            help="Filter by specific team members"
        )
        
        # Status filter with colored chips
        statuses = sorted(df['Status'].unique().tolist())
        selected_statuses = st.multiselect(
            "📊 Status",
            statuses,
            default=statuses
        )
        
        # Priority filter
        priorities = sorted(df['Priority'].unique().tolist())
        selected_priorities = st.multiselect(
            "⚡ Priority",
            priorities,
            default=priorities
        )
        
        # Date range
        st.markdown("---")
        st.markdown("### 📅 Date Range")
        
        if 'Created' in df.columns and not df['Created'].isnull().all():
            min_date = df['Created'].min().date()
            max_date = datetime.now().date()
            date_range = st.date_input(
                "Select Range",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📥 Export Report", width="stretch"):
            st.info("Export functionality would be available here")
        
        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    # Apply filters
    mask = (
        df['Assignee'].isin(selected_assignees) & 
        df['Status'].isin(selected_statuses) &
        df['Priority'].isin(selected_priorities)
    )
    
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        mask &= (df['Created'].dt.date >= start_date) & (df['Created'].dt.date <= end_date)
    
    filtered_df = df[mask]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # === KPI Section ===
    total_tickets = len(filtered_df)
    completed = len(filtered_df[filtered_df['Status'].isin(done_statuses)])
    in_progress = len(filtered_df[filtered_df['Status'].isin(in_progress_statuses)])
    todo = len(filtered_df[filtered_df['Status'].isin(todo_statuses)])
    completion_rate = (completed / total_tickets * 100) if total_tickets > 0 else 0
    
    # Average resolution time
    resolved_df = filtered_df[filtered_df['Resolution Days'].notna()]
    avg_resolution = resolved_df['Resolution Days'].mean() if not resolved_df.empty else 0
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Issues", 
            total_tickets,
            f"📋 All tickets",
            "neutral"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Completed",
            completed,
            f"✅ {completion_rate:.1f}% rate",
            "positive" if completion_rate > 60 else "negative"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "In Progress",
            in_progress,
            f"🔄 Active work",
            "neutral"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "To Do",
            todo,
            f"📝 Backlog",
            "negative" if todo > 20 else "neutral"
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(create_metric_card(
            "Avg Resolution",
            f"{avg_resolution:.1f}d" if avg_resolution > 0 else "N/A",
            f"⏱️ Days to close",
            "positive" if avg_resolution < 5 else "negative"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === Tabs for Different Views ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "👤 Individual Performance", 
        "📈 Trends & Analytics",
        "📋 Detailed View"
    ])
    
    # === TAB 1: Overview ===
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="section-header">📊 Workload Distribution</div>', unsafe_allow_html=True)
            
            workload = filtered_df.groupby('Assignee').agg({
                'Issue key': 'count',
                'Status': lambda x: (x.isin(done_statuses)).sum()
            }).reset_index()
            workload.columns = ['Assignee', 'Total', 'Completed']
            workload = workload.sort_values('Total', ascending=True)
            
            fig_workload = go.Figure()
            fig_workload.add_trace(go.Bar(
                name='Completed',
                y=workload['Assignee'],
                x=workload['Completed'],
                orientation='h',
                marker_color='#48bb78',
                text=workload['Completed'],
                textposition='inside'
            ))
            fig_workload.add_trace(go.Bar(
                name='Remaining',
                y=workload['Assignee'],
                x=workload['Total'] - workload['Completed'],
                orientation='h',
                marker_color='#667eea',
                text=workload['Total'] - workload['Completed'],
                textposition='inside'
            ))
            
            fig_workload.update_layout(
                barmode='stack',
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a0aec0'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_workload, width="stretch")
        
        with col_right:
            render_leaderboard(filtered_df, done_statuses)
        
        # Second row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="section-header">📌 Status Distribution</div>', unsafe_allow_html=True)
            status_dist = filtered_df['Status'].value_counts().reset_index()
            status_dist.columns = ['Status', 'Count']
            
            colors = ['#48bb78', '#667eea', '#f6ad55', '#fc8181', '#b794f4', '#68d391']
            
            fig_status = px.pie(
                status_dist, 
                values='Count', 
                names='Status',
                hole=0.5,
                color_discrete_sequence=colors
            )
            fig_status.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a0aec0'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                margin=dict(l=20, r=20, t=20, b=60),
                height=300
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, width="stretch")
        
        with col2:
            st.markdown('<div class="section-header">⚡ Priority Breakdown</div>', unsafe_allow_html=True)
            priority_dist = filtered_df['Priority'].value_counts().reset_index()
            priority_dist.columns = ['Priority', 'Count']
            
            priority_colors = {
                'Highest': '#fc8181',
                'High': '#f6ad55',
                'Medium': '#68d391',
                'Low': '#4fd1c5',
                'Lowest': '#667eea'
            }
            
            fig_priority = px.bar(
                priority_dist,
                x='Priority',
                y='Count',
                color='Priority',
                color_discrete_map=priority_colors,
                text='Count'
            )
            fig_priority.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a0aec0'),
                showlegend=False,
                margin=dict(l=0, r=0, t=20, b=0),
                height=300,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            fig_priority.update_traces(textposition='outside')
            st.plotly_chart(fig_priority, width="stretch")
        
        with col3:
            st.markdown('<div class="section-header">🏷️ Issue Types</div>', unsafe_allow_html=True)
            type_dist = filtered_df['Issue Type'].value_counts().reset_index()
            type_dist.columns = ['Type', 'Count']
            
            fig_type = px.pie(
                type_dist,
                values='Count',
                names='Type',
                hole=0.5,
                color_discrete_sequence=['#667eea', '#b794f4', '#f6ad55', '#fc8181']
            )
            fig_type.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a0aec0'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                margin=dict(l=20, r=20, t=20, b=60),
                height=300
            )
            st.plotly_chart(fig_type, width="stretch")
    
    # === TAB 2: Individual Performance ===
    with tab2:
        st.markdown('<div class="section-header">👤 Individual Performance Analysis</div>', unsafe_allow_html=True)
        
        # Select person
        col_select, col_compare = st.columns([1, 1])
        
        with col_select:
            target_person = st.selectbox(
                "🎯 Select Team Member",
                assignees,
                index=assignees.index("Vidhya sagar") if "Vidhya sagar" in assignees else 0
            )
        
        with col_compare:
            compare_person = st.selectbox(
                "🔄 Compare With (Optional)",
                ["None"] + assignees,
                index=0
            )
        
        # Get person data
        person_df = df[df['Assignee'] == target_person]
        
        if not person_df.empty:
            p_total = len(person_df)
            p_done = len(person_df[person_df['Status'].isin(done_statuses)])
            p_progress = len(person_df[person_df['Status'].isin(in_progress_statuses)])
            p_efficiency = (p_done / p_total * 100) if p_total > 0 else 0
            
            # Avg resolution for person
            p_resolved = person_df[person_df['Resolution Days'].notna()]
            p_avg_resolution = p_resolved['Resolution Days'].mean() if not p_resolved.empty else 0
            
            # Person metrics
            st.markdown(f"### 📊 {target_person}'s Performance")
            
            m1, m2, m3, m4, m5 = st.columns(5)
            
            with m1:
                st.metric("Total Assigned", p_total)
            with m2:
                st.metric("Completed", p_done, delta=f"{p_efficiency:.0f}% efficiency")
            with m3:
                st.metric("In Progress", p_progress)
            with m4:
                st.metric("Avg Resolution", f"{p_avg_resolution:.1f} days" if p_avg_resolution > 0 else "N/A")
            with m5:
                # Calculate rank
                completed_counts = df[df['Status'].isin(done_statuses)].groupby('Assignee').size().sort_values(ascending=False)
                rank = list(completed_counts.index).index(target_person) + 1 if target_person in completed_counts.index else "N/A"
                st.metric("Team Rank", f"#{rank}")
            
            # Person's charts
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("#### 📈 Status Breakdown")
                p_status = person_df['Status'].value_counts().reset_index()
                p_status.columns = ['Status', 'Count']
                
                fig_p_status = px.bar(
                    p_status,
                    x='Status',
                    y='Count',
                    color='Status',
                    color_discrete_sequence=['#48bb78', '#667eea', '#f6ad55', '#fc8181', '#b794f4']
                )
                fig_p_status.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#a0aec0'),
                    showlegend=False,
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_p_status, width="stretch")
            
            with col_right:
                st.markdown("#### ⏱️ Activity Timeline")
                if 'Created' in person_df.columns:
                    p_timeline = person_df.groupby(person_df['Created'].dt.date).size().reset_index(name='Count')
                    p_timeline.columns = ['Date', 'Count']
                    
                    fig_timeline = px.area(
                        p_timeline,
                        x='Date',
                        y='Count',
                        color_discrete_sequence=['#667eea']
                    )
                    fig_timeline.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#a0aec0'),
                        height=300,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                    )
                    st.plotly_chart(fig_timeline, width="stretch")
            
            # Recent tickets
            st.markdown("#### 📋 Recent Tickets")
            display_cols = ['Issue key', 'Summary', 'Status', 'Priority', 'Created']
            display_cols = [c for c in display_cols if c in person_df.columns]
            
            st.dataframe(
                person_df[display_cols].sort_values('Created', ascending=False).head(10),
                width="stretch",
                hide_index=True
            )
            
            # Comparison section
            if compare_person != "None":
                st.markdown("---")
                st.markdown(f"### 🔄 Comparison: {target_person} vs {compare_person}")
                
                compare_df = df[df['Assignee'] == compare_person]
                
                if not compare_df.empty:
                    c_total = len(compare_df)
                    c_done = len(compare_df[compare_df['Status'].isin(done_statuses)])
                    c_efficiency = (c_done / c_total * 100) if c_total > 0 else 0
                    
                    comparison_data = pd.DataFrame({
                        'Metric': ['Total Tickets', 'Completed', 'Efficiency %'],
                        target_person: [p_total, p_done, round(p_efficiency, 1)],
                        compare_person: [c_total, c_done, round(c_efficiency, 1)]
                    })
                    
                    fig_compare = go.Figure()
                    fig_compare.add_trace(go.Bar(
                        name=target_person,
                        x=comparison_data['Metric'],
                        y=comparison_data[target_person],
                        marker_color='#667eea'
                    ))
                    fig_compare.add_trace(go.Bar(
                        name=compare_person,
                        x=comparison_data['Metric'],
                        y=comparison_data[compare_person],
                        marker_color='#b794f4'
                    ))
                    fig_compare.update_layout(
                        barmode='group',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#a0aec0'),
                        height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02)
                    )
                    st.plotly_chart(fig_compare, width="stretch")
    
    # === TAB 3: Trends & Analytics ===
    with tab3:
        st.markdown('<div class="section-header">📈 Trends & Deep Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Weekly Activity Trend")
            if 'Created' in filtered_df.columns:
                weekly = filtered_df.groupby(filtered_df['Created'].dt.isocalendar().week).agg({
                    'Issue key': 'count',
                    'Status': lambda x: (x.isin(done_statuses)).sum()
                }).reset_index()
                weekly.columns = ['Week', 'Created', 'Resolved']
                
                fig_weekly = go.Figure()
                fig_weekly.add_trace(go.Scatter(
                    x=weekly['Week'],
                    y=weekly['Created'],
                    mode='lines+markers',
                    name='Created',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                fig_weekly.add_trace(go.Scatter(
                    x=weekly['Week'],
                    y=weekly['Resolved'],
                    mode='lines+markers',
                    name='Resolved',
                    line=dict(color='#48bb78', width=3),
                    marker=dict(size=8)
                ))
                fig_weekly.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#a0aec0'),
                    height=350,
                    xaxis=dict(title='Week Number', showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_weekly, width="stretch")
        
        with col2:
            st.markdown("#### ⏱️ Resolution Time Distribution")
            if 'Resolution Days' in filtered_df.columns:
                resolution_data = filtered_df[filtered_df['Resolution Days'].notna()]['Resolution Days']
                
                if not resolution_data.empty:
                    fig_resolution = px.histogram(
                        resolution_data,
                        nbins=20,
                        color_discrete_sequence=['#667eea']
                    )
                    fig_resolution.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#a0aec0'),
                        height=350,
                        xaxis=dict(title='Days to Resolve', showgrid=False),
                        yaxis=dict(title='Count', showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                        showlegend=False
                    )
                    st.plotly_chart(fig_resolution, width="stretch")
                else:
                    st.info("No resolution time data available")
        
        # Heatmap
        st.markdown("#### 🗓️ Activity Heatmap by Day")
        if 'Created' in filtered_df.columns:
            heatmap_data = filtered_df.copy()
            heatmap_data['DayOfWeek'] = heatmap_data['Created'].dt.day_name()
            heatmap_data['Week'] = heatmap_data['Created'].dt.isocalendar().week
            
            pivot = heatmap_data.groupby(['DayOfWeek', 'Week']).size().reset_index(name='Count')
            pivot_table = pivot.pivot(index='DayOfWeek', columns='Week', values='Count').fillna(0)
            
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot_table = pivot_table.reindex([d for d in days_order if d in pivot_table.index])
            
            fig_heatmap = px.imshow(
                pivot_table,
                color_continuous_scale='Viridis',
                aspect='auto'
            )
            fig_heatmap.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a0aec0'),
                height=300,
                xaxis=dict(title='Week Number'),
                yaxis=dict(title='')
            )
            st.plotly_chart(fig_heatmap, width="stretch")
        
        # Reporter Analysis
        st.markdown("#### 👤 Reporter Analysis (Who Creates Most Tickets)")
        reporter_dist = filtered_df['Reporter'].value_counts().head(10).reset_index()
        reporter_dist.columns = ['Reporter', 'Count']
        
        fig_reporter = px.bar(
            reporter_dist,
            x='Count',
            y='Reporter',
            orientation='h',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig_reporter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a0aec0'),
            height=350,
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_reporter, width="stretch")
    
    # === TAB 4: Detailed View ===
    with tab4:
        st.markdown('<div class="section-header">📋 All Tickets - Detailed View</div>', unsafe_allow_html=True)
        
        # Search
        search = st.text_input("🔍 Search tickets by summary or key...")
        
        display_df = filtered_df.copy()
        if search:
            display_df = display_df[
                display_df['Summary'].str.contains(search, case=False, na=False) |
                display_df['Issue key'].str.contains(search, case=False, na=False)
            ]
        
        # Display columns
        cols_to_show = ['Issue key', 'Summary', 'Assignee', 'Status', 'Priority', 'Issue Type', 'Created', 'Updated']
        cols_to_show = [c for c in cols_to_show if c in display_df.columns]
        
        st.dataframe(
            display_df[cols_to_show].sort_values('Created', ascending=False),
            width="stretch",
            hide_index=True,
            height=500
        )
        
        st.markdown(f"**Showing {len(display_df)} of {len(filtered_df)} tickets**")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #a0aec0; padding: 20px;'>
            <p>🚀 Team Leads Dashboard • Built with Streamlit & Plotly</p>
            <p style='font-size: 0.8rem;'>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
