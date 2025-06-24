import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Amazon Keyword Performance AI Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #333333;
        font-weight: 500;
    }
    .user-message {
        background-color: #e8f4fd;
        border-left: 4px solid #2196f3;
        color: #1a1a1a;
    }
    .bot-message {
        background-color: #f0f8ff;
        border-left: 4px solid #4caf50;
        color: #1a1a1a;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #1565c0;
    }
    /* Improve text readability in chat messages */
    .chat-message strong {
        color: #2c3e50;
    }
    /* Better contrast for code blocks */
    .stCodeBlock {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None

def send_chat_message(message):
    """Send a message to the chat API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message},
            timeout=30
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def get_performance_summary():
    """Get performance summary from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/summary", timeout=10)
        return response.status_code == 200, response.json()
    except:
        return False, {}

def get_top_keywords(metric="purchases", limit=10):
    """Get top keywords by metric"""
    try:
        response = requests.get(f"{API_BASE_URL}/keywords/top/{metric}?limit={limit}", timeout=10)
        return response.status_code == 200, response.json()
    except:
        return False, {}

def create_performance_charts(data):
    """Create performance visualization charts"""
    if not data or not isinstance(data, list) or len(data) == 0:
        return None, None, None
    
    df = pd.DataFrame(data)
    
    # Top keywords by purchases
    if 'purchases' in df.columns:
        fig_purchases = px.bar(
            df.head(10), 
            x='keyword', 
            y='purchases',
            title="Top 10 Keywords by Purchases",
            color='purchases',
            color_continuous_scale='viridis'
        )
        fig_purchases.update_layout(xaxis_tickangle=-45)
    else:
        fig_purchases = None
    
    # CTR vs Conversion Rate scatter plot
    if all(col in df.columns for col in ['ctr', 'conversion_rate']):
        fig_scatter = px.scatter(
            df, 
            x='ctr', 
            y='conversion_rate',
            title="CTR vs Conversion Rate",
            hover_data=['keyword'],
            size='impressions',
            color='purchases'
        )
    else:
        fig_scatter = None
    
    # Performance metrics distribution
    if 'impressions' in df.columns:
        fig_dist = px.histogram(
            df, 
            x='impressions',
            title="Distribution of Impressions",
            nbins=20
        )
    else:
        fig_dist = None
    
    return fig_purchases, fig_scatter, fig_dist

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Amazon Keyword Performance AI Chatbot</h1>', unsafe_allow_html=True)
    
    # Check API health
    api_healthy, health_data = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ API server is not running. Please start the backend server first.")
        st.info("To start the server, run: `python api/main.py`")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Quick Actions")
        
        # Performance Summary
        if st.button("📈 Performance Summary"):
            success, summary_data = get_performance_summary()
            if success:
                st.session_state.summary_data = summary_data
                st.session_state.show_summary = True
            else:
                st.error("Failed to fetch summary data")
        
        # Top Keywords
        st.subheader("🏆 Top Keywords")
        metric = st.selectbox("Metric", ["purchases", "impressions", "clicks", "ctr", "conversion_rate"])
        limit = st.slider("Number of results", 5, 50, 10)
        
        if st.button(f"Get Top {limit} by {metric}"):
            success, top_data = get_top_keywords(metric, limit)
            if success:
                st.session_state.top_keywords = top_data
                st.session_state.show_top_keywords = True
            else:
                st.error("Failed to fetch top keywords")
        
        # API Status
        st.subheader("🔍 API Status")
        if api_healthy:
            st.success("✅ Connected")
            if health_data:
                st.write(f"**Total Keywords:** {health_data.get('data_summary', {}).get('total_keywords', 'N/A')}")
        else:
            st.error("❌ Disconnected")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with AI Analyst")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">👤 **You:** {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message">🤖 **AI:** {message["content"]}</div>', unsafe_allow_html=True)
                    
                    # Display data if available
                    if "data" in message and message["data"]:
                        with st.expander("📊 View Data"):
                            df = pd.DataFrame(message["data"])
                            st.dataframe(df, use_container_width=True)
                    
                    # Display SQL query if available
                    if "sql_query" in message and message["sql_query"]:
                        with st.expander("🔍 Generated SQL"):
                            st.code(message["sql_query"], language="sql")
        
        # Chat input
        user_input = st.text_area("Ask about your keyword performance:", height=100, placeholder="e.g., 'Show me top 10 keywords by conversion rate' or 'Which keywords are underperforming?'")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Send Message", type="primary"):
                if user_input.strip():
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # Get AI response
                    with st.spinner("🤖 AI is analyzing your data..."):
                        success, response = send_chat_message(user_input)
                    
                    if success:
                        # Add AI response to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response.get("response", "Sorry, I couldn't process your request."),
                            "data": response.get("data"),
                            "sql_query": response.get("sql_query"),
                            "insights": response.get("insights")
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Sorry, I encountered an error: {response.get('error', 'Unknown error')}"
                        })
                    
                    st.rerun()
        
        with col2:
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.header("📊 Quick Insights")
        
        # Show summary if available
        if hasattr(st.session_state, 'show_summary') and st.session_state.show_summary:
            summary = st.session_state.summary_data
            if summary:
                st.subheader("📈 Performance Summary")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Keywords", f"{summary.get('total_keywords', 0):,}")
                    st.metric("Avg CTR", f"{summary.get('avg_ctr', 0):.2%}")
                
                with col2:
                    st.metric("Total Impressions", f"{summary.get('total_impressions', 0):,}")
                    st.metric("Avg Conversion", f"{summary.get('avg_conversion_rate', 0):.2%}")
        
        # Show top keywords if available
        if hasattr(st.session_state, 'show_top_keywords') and st.session_state.show_top_keywords:
            top_data = st.session_state.top_keywords
            if top_data and 'results' in top_data:
                st.subheader(f"🏆 Top {len(top_data['results'])} Keywords")
                
                df = pd.DataFrame(top_data['results'])
                if not df.empty:
                    # Create a simple bar chart
                    fig = px.bar(
                        df.head(5), 
                        x='keyword', 
                        y=top_data.get('metric', 'purchases'),
                        title=f"Top 5 by {top_data.get('metric', 'purchases')}"
                    )
                    fig.update_layout(xaxis_tickangle=-45, height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data table
                    with st.expander("View All Results"):
                        st.dataframe(df, use_container_width=True)
        
        # Sample questions
        st.subheader("💡 Sample Questions")
        sample_questions = [
            "Show me top 10 keywords by purchases",
            "Which keywords have the highest conversion rate?",
            "Find keywords with low CTR but high impressions",
            "What's the average performance across all keywords?",
            "Show me keywords containing 'wireless'",
            "Which keywords are underperforming?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question[:20]}"):
                st.session_state.messages.append({"role": "user", "content": question})
                with st.spinner("🤖 AI is analyzing..."):
                    success, response = send_chat_message(question)
                if success:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response.get("response", "Sorry, I couldn't process your request."),
                        "data": response.get("data"),
                        "sql_query": response.get("sql_query")
                    })
                st.rerun()

if __name__ == "__main__":
    main() 