# 🚀 Quick Start Guide

## Prerequisites

- Python 3.8+
- Snowflake account
- Git

## Installation

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

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your Snowflake credentials
   ```

## Configuration

Edit your `.env` file with your Snowflake credentials:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=NEWS_SENTIMENT
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## Testing

Run the test script to verify everything works:

```bash
python test_scraper.py
```

## Database Setup

Initialize your Snowflake database:

```bash
python scripts/setup_database.py
```

## Running the Scraper

### Manual Run
```bash
python src/main.py
```

### Automated Scheduling
```bash
# Run immediately and start scheduler
python src/scheduler.py --run-now

# Start scheduler only
python src/scheduler.py

# Test mode (hourly runs)
python src/scheduler.py --test
```

## Dashboard

Start the Streamlit dashboard:

```bash
streamlit run src/dashboard.py
```

## Project Structure

```
news-sentiment-scraper/
├── src/
│   ├── scrapers/          # News scraping modules
│   ├── sentiment/         # Sentiment analysis engines
│   ├── database/          # Snowflake integration
│   ├── models/            # Data models
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
├── env.example
├── .gitignore
├── README.md
└── QUICKSTART.md
```

## Features

- ✅ **Free News Sources**: RSS feeds from major financial news sites
- ✅ **Multi-Engine Sentiment Analysis**: TextBlob, VADER, NLTK
- ✅ **Snowflake Integration**: Enterprise-grade data warehouse
- ✅ **Automated Scheduling**: Daily sentiment collection
- ✅ **Real-time Dashboard**: Streamlit visualization
- ✅ **Scalable Architecture**: Easy to upgrade to paid APIs

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the virtual environment
2. **Snowflake Connection**: Verify your credentials in `.env`
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Permission Errors**: Check file permissions on Windows

### Logs

Check the logs directory for detailed error messages:
```bash
tail -f logs/scraper.log
```

## Next Steps

1. **Scale Up**: Add paid news APIs (NewsAPI, Alpha Vantage)
2. **Advanced NLP**: Integrate Hugging Face transformers
3. **Cloud Deployment**: Deploy to AWS/GCP/Azure
4. **Real-time Processing**: Add Apache Kafka
5. **Machine Learning**: Build predictive models

## Support

- Check the main README.md for detailed documentation
- Review the logs for error messages
- Ensure all dependencies are installed correctly 