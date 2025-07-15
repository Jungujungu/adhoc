# Fortune 100 News Sentiment Scraper

A comprehensive news sentiment analysis system that scrapes and analyzes news sentiment for the top 100 Fortune companies using free sources and stores data in Snowflake.

## 🚀 Features

- **Free News Sources**: RSS feeds, Reddit, Twitter, and web scraping
- **Sentiment Analysis**: Multiple sentiment analysis engines (TextBlob, VADER, NLTK)
- **Snowflake Integration**: Enterprise-grade data warehouse storage
- **Automated Scheduling**: Daily sentiment collection and analysis
- **Real-time Dashboard**: Streamlit-based visualization
- **Scalable Architecture**: Easy to upgrade to paid APIs later

## 📋 Prerequisites

- Python 3.8+
- Snowflake account
- Reddit API credentials (optional)
- Twitter API credentials (optional)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd news-sentiment-scraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Configure Snowflake**
   - Update `config/snowflake_config.py` with your Snowflake credentials
   - Run the database setup script: `python scripts/setup_database.py`

## 🔧 Configuration

### Environment Variables (.env)
```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# API Keys (Optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_token

# Application Settings
LOG_LEVEL=INFO
SCRAPING_DELAY=2
MAX_RETRIES=3
```

## 📊 Usage

### 1. Run the Scraper
```bash
python src/main.py
```

### 2. Start the Dashboard
```bash
streamlit run src/dashboard.py
```

### 3. Schedule Daily Runs
```bash
python src/scheduler.py
```

## 🏗️ Project Structure

```
news-sentiment-scraper/
├── src/
│   ├── scrapers/          # News scraping modules
│   ├── sentiment/         # Sentiment analysis engines
│   ├── database/          # Snowflake integration
│   ├── models/            # Data models
│   ├── utils/             # Utility functions
│   ├── main.py           # Main scraper
│   ├── scheduler.py      # Task scheduler
│   └── dashboard.py      # Streamlit dashboard
├── config/
│   ├── companies.py      # Fortune 100 companies list
│   └── snowflake_config.py
├── scripts/
│   └── setup_database.py
├── tests/
├── data/
├── logs/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 📈 Data Flow

1. **News Collection**: Scrapers collect news from multiple sources
2. **Text Processing**: Clean and preprocess news text
3. **Sentiment Analysis**: Analyze sentiment using multiple engines
4. **Data Storage**: Store results in Snowflake
5. **Visualization**: Display insights via dashboard

## 🔍 Sentiment Analysis

The system uses multiple sentiment analysis engines:

- **TextBlob**: General-purpose sentiment analysis
- **VADER**: Social media optimized sentiment
- **NLTK**: Advanced NLP capabilities

## 📊 Dashboard Features

- Real-time sentiment trends
- Company-specific sentiment analysis
- Historical sentiment tracking
- News source distribution
- Sentiment correlation analysis

## 🚀 Scaling Up

When ready to scale, consider:

1. **Paid News APIs**: NewsAPI, Alpha Vantage, Finnhub
2. **Advanced NLP**: Hugging Face transformers
3. **Cloud Deployment**: AWS/GCP/Azure
4. **Real-time Processing**: Apache Kafka
5. **Advanced Analytics**: Machine learning models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please respect:
- Rate limits of news sources
- Terms of service of APIs
- Robots.txt files when web scraping
- Data privacy and usage rights

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information 