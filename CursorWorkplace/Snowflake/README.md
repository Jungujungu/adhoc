# Amazon Keyword Performance AI Chatbot

An intelligent AI chatbot powered by Claude that analyzes Amazon keyword performance data stored in Snowflake. Ask natural language questions about your keyword performance and get actionable insights.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about your keyword performance
- **AI-Powered Analysis**: Uses Claude 3.5 Sonnet for intelligent data analysis and insights
- **Real-time Data**: Direct connection to Snowflake for live data analysis
- **Interactive Dashboard**: Beautiful Streamlit interface with charts and visualizations
- **SQL Generation**: Automatically converts natural language to SQL queries
- **Performance Metrics**: Track impressions, clicks, purchases, CTR, and conversion rates

## 📊 Sample Questions You Can Ask

- "Show me top 10 keywords by purchases"
- "Which keywords have the highest conversion rate?"
- "Find keywords with low CTR but high impressions"
- "What's the average performance across all keywords?"
- "Show me keywords containing 'wireless'"
- "Which keywords are underperforming?"
- "Calculate the correlation between keyword length and performance"
- "Identify seasonal patterns in keyword performance"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   Snowflake     │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Claude AI     │
                       │   (Anthropic)   │
                       └─────────────────┘
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Snowflake account with Amazon keyword data
- Anthropic API key for Claude

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd Snowflake
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `env_example.txt` to `.env` and fill in your credentials:

```bash
cp env_example.txt .env
```

Edit `.env` with your actual values:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
KEYWORD_TABLE=amazon_keywords

# Claude API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 3. Prepare Your Snowflake Data

Your Snowflake table should have the following structure:

```sql
CREATE TABLE amazon_keywords (
    keyword VARCHAR,
    impressions NUMBER,
    clicks NUMBER,
    purchases NUMBER,
    -- Add other relevant columns as needed
);
```

### 4. Start the Backend Server

```bash
cd api
python main.py
```

The API server will start on `http://localhost:8000`

### 5. Start the Frontend

In a new terminal:

```bash
cd frontend
streamlit run streamlit_app.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
Snowflake/
├── api/
│   └── main.py                 # FastAPI backend server
├── database/
│   └── snowflake_client.py     # Snowflake database client
├── ai/
│   └── claude_client.py        # Claude AI integration
├── frontend/
│   └── streamlit_app.py        # Streamlit frontend
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── env_example.txt            # Environment variables template
└── README.md                  # This file
```

## 🔧 API Endpoints

### Chat Endpoint
- **POST** `/chat` - Send natural language queries
- **Request**: `{"message": "Show me top keywords by purchases"}`
- **Response**: Analysis, data, SQL query, and insights

### Data Endpoints
- **GET** `/summary` - Get performance summary
- **GET** `/keywords/top/{metric}` - Get top keywords by metric
- **GET** `/keywords/search/{term}` - Search keywords
- **GET** `/schema` - Get table schema
- **GET** `/health` - Health check

## 💡 Usage Examples

### 1. Performance Analysis
```
User: "Show me keywords with conversion rate above 5%"
AI: Analyzes data and provides insights about high-converting keywords
```

### 2. Trend Analysis
```
User: "Which keywords are declining in performance?"
AI: Identifies keywords with decreasing metrics over time
```

### 3. Optimization Recommendations
```
User: "What should I optimize for better performance?"
AI: Provides actionable recommendations based on data analysis
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Error**: Check your Snowflake credentials and network connectivity
2. **API Key Error**: Verify your Anthropic API key is correct
3. **Table Not Found**: Ensure your table name matches the `KEYWORD_TABLE` environment variable
4. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Debug Mode

Enable debug logging by setting the log level in the code:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Local Development
- Backend: `python api/main.py`
- Frontend: `streamlit run frontend/streamlit_app.py`

### Production Deployment
- Use a production WSGI server like Gunicorn for the FastAPI backend
- Deploy Streamlit to Streamlit Cloud or similar platform
- Use environment variables for all sensitive configuration
- Implement proper authentication and authorization

## 📈 Performance Optimization

- Use connection pooling for Snowflake connections
- Implement caching for frequently accessed data
- Optimize SQL queries with proper indexing
- Use async/await for better concurrency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation at `http://localhost:8000/docs`
- Open an issue in the repository

## 🔮 Future Enhancements

- [ ] Add time-series analysis capabilities
- [ ] Implement keyword clustering and categorization
- [ ] Add competitor analysis features
- [ ] Create automated reporting and alerts
- [ ] Add more visualization options
- [ ] Implement user authentication and multi-tenant support 