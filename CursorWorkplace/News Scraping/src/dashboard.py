"""
News Sentiment Dashboard
Streamlit dashboard for Fortune 100 news sentiment analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.snowflake_manager import SnowflakeManager
from config.companies import FORTUNE_100_COMPANIES

# Page configuration
st.set_page_config(
    page_title="Fortune 100 News Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive { color: #28a745; }
    .negative { color: #dc3545; }
    .neutral { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Fortune 100 News Sentiment Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Date range selector
    st.sidebar.subheader("📅 Date Range")
    days_back = st.sidebar.slider("Days to analyze", 1, 30, 7)
    
    # Company selector
    st.sidebar.subheader("🏢 Company Filter")
    companies = [company['name'] for company in FORTUNE_100_COMPANIES]
    selected_companies = st.sidebar.multiselect(
        "Select companies to analyze",
        companies,
        default=companies[:10]  # Default to first 10 companies
    )
    
    # Load data
    try:
        with SnowflakeManager() as db_manager:
            # Get daily sentiment data
            daily_data = db_manager.get_daily_sentiment_data(days_back)
            
            # Get top companies
            top_companies = db_manager.get_top_companies_by_sentiment(days_back, 10)
            
            # Get sector sentiment
            sector_data = db_manager.get_sector_sentiment(days_back)
            
            # Get article count by source
            source_data = db_manager.get_article_count_by_source(days_back)
            
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("💡 Make sure your Snowflake database is properly configured and running.")
        return
    
    # Main content
    if daily_data.empty:
        st.warning("⚠️ No data available for the selected time period.")
        st.info("💡 Try running the scraper first to collect some data.")
        return
    
    # Key Metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_articles = len(daily_data)
        st.metric("Total Articles", total_articles)
    
    with col2:
        avg_sentiment = daily_data['avg_sentiment_score'].mean()
        st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
    
    with col3:
        positive_articles = len(daily_data[daily_data['sentiment_label'] == 'positive'])
        st.metric("Positive Articles", positive_articles)
    
    with col4:
        negative_articles = len(daily_data[daily_data['sentiment_label'] == 'negative'])
        st.metric("Negative Articles", negative_articles)
    
    # Charts
    st.subheader("📊 Sentiment Analysis")
    
    # Top companies by sentiment
    if not top_companies.empty:
        st.subheader("🏆 Top Companies by Sentiment")
        
        fig = px.bar(
            top_companies.head(10),
            x='avg_sentiment',
            y='company_name',
            orientation='h',
            title="Top 10 Companies by Average Sentiment",
            labels={'avg_sentiment': 'Average Sentiment Score', 'company_name': 'Company'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily sentiment trends
    if not daily_data.empty:
        st.subheader("📈 Daily Sentiment Trends")
        
        # Filter by selected companies
        if selected_companies:
            filtered_data = daily_data[daily_data['company_name'].isin(selected_companies)]
        else:
            filtered_data = daily_data
        
        fig = px.line(
            filtered_data,
            x='date',
            y='avg_sentiment_score',
            color='company_name',
            title="Sentiment Trends Over Time",
            labels={'avg_sentiment_score': 'Sentiment Score', 'date': 'Date', 'company_name': 'Company'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Sector analysis
    if not sector_data.empty:
        st.subheader("🏭 Sector Sentiment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                sector_data,
                x='sector',
                y='sector_sentiment',
                title="Average Sentiment by Sector",
                labels={'sector_sentiment': 'Average Sentiment', 'sector': 'Sector'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(
                sector_data,
                values='total_articles',
                names='sector',
                title="Article Distribution by Sector"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # News source analysis
    if not source_data.empty:
        st.subheader("📰 News Source Analysis")
        
        fig = px.bar(
            source_data,
            x='source',
            y='article_count',
            title="Articles by News Source",
            labels={'article_count': 'Number of Articles', 'source': 'News Source'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data table
    st.subheader("📋 Detailed Data")
    
    if selected_companies:
        table_data = daily_data[daily_data['company_name'].isin(selected_companies)]
    else:
        table_data = daily_data
    
    # Add color coding for sentiment
    def color_sentiment(val):
        if val == 'positive':
            return 'background-color: #d4edda'
        elif val == 'negative':
            return 'background-color: #f8d7da'
        else:
            return 'background-color: #e2e3e5'
    
    styled_table = table_data.style.applymap(color_sentiment, subset=['sentiment_label'])
    st.dataframe(styled_table, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📊 Fortune 100 News Sentiment Analysis Dashboard</p>
        <p>Data updated automatically from RSS feeds and sentiment analysis engines</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 