# AI-Powered NYC Tech Events Aggregator

An intelligent system that automatically collects, processes, and serves technology-related events from multiple platforms in New York City.

## 🎯 Project Goal

Build an AI-powered aggregator that collects tech events from Eventbrite, Meetup, Luma, and Partiful, then uses AI to filter and classify them into a unified, searchable database.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  AI Processing  │    │   Web Interface │
│                 │    │                 │    │                 │
│ • Eventbrite    │───▶│ • Classification │───▶│ • Streamlit UI  │
│ • Meetup        │    │ • Filtering     │    │ • REST API      │
│ • Luma          │    │ • Normalization │    │ • Search        │
│ • Partiful      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Raw Data       │    │  PostgreSQL     │    │  Users          │
│  Storage        │    │  Database       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
ai_events_aggregator/
├── src/
│   ├── ingestion/     # Data collection from APIs/scrapers
│   ├── processing/    # Data cleaning and normalization
│   ├── storage/       # Database operations
│   ├── api/          # REST API endpoints
│   └── frontend/     # Streamlit web interface
├── data/             # Raw and processed data files
├── logs/             # Application logs
├── notebooks/        # Jupyter notebooks for analysis
└── venv/             # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for database storage)
- API keys for Eventbrite, Meetup, OpenAI, and Apify

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dgupta2003/ai_event_aggregator.git
   cd ai_event_aggregator
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual API keys
   ```

5. **Run the application**
   ```bash
   # Start the web interface
   streamlit run src/frontend/app.py
   
   # Or run data collection
   python src/ingestion/fetch_all.py
   ```

## 🔧 Development Phases

### ✅ Phase 0: Setup & Planning
- [x] Project structure created
- [x] Virtual environment set up
- [x] Dependencies installed
- [x] Git repository initialized

### 📋 Phase 1: Requirements & Scope
- [ ] Define target platforms and data sources
- [ ] Create standardized event data schema
- [ ] Document expected outputs

### 🔍 Phase 2: Data Ingestion
- [ ] Eventbrite API integration
- [ ] Meetup API integration
- [ ] Luma scraping (via Apify)
- [ ] Partiful scraping (via Apify)

### 🧹 Phase 3: Data Processing
- [ ] Data normalization and cleaning
- [ ] Deduplication logic
- [ ] Standardized output format

### 🤖 Phase 4: AI Classification
- [ ] Keyword-based filtering
- [ ] OpenAI integration for semantic classification
- [ ] Event categorization

### 💾 Phase 5: Database Storage
- [ ] PostgreSQL setup
- [ ] Database schema design
- [ ] Data insertion and querying

### 🌐 Phase 6: API Layer
- [ ] FastAPI setup
- [ ] REST endpoints
- [ ] CORS and pagination

### 🎨 Phase 7: Frontend
- [ ] Streamlit interface
- [ ] Event filtering and search
- [ ] Map visualization

### ⚡ Phase 8: Automation
- [ ] Scheduled data collection
- [ ] Error handling and alerts
- [ ] Data freshness management

## 🛠️ Technologies Used

- **Python 3.8+** - Core programming language
- **Pandas** - Data manipulation and analysis
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **FastAPI** - REST API framework
- **Streamlit** - Web interface
- **OpenAI API** - AI-powered classification
- **Playwright** - Web scraping
- **Requests** - HTTP API calls

## 📊 Data Sources

| Platform | Method | API Rate Limits | Data Fields |
|----------|--------|----------------|-------------|
| Eventbrite | API | 1000/hour | Title, Description, Date, Venue, Category |
| Meetup | API | 200/hour | Name, Description, Time, Location, Group |
| Luma | Scraping | N/A | Title, Date, Location, Description |
| Partiful | Scraping | N/A | Event Name, Date, Venue, Details |

## 🔑 Required API Keys

You'll need to register for these services:

1. **Eventbrite** - [developer.eventbrite.com](https://developer.eventbrite.com)
2. **Meetup** - [secure.meetup.com/meetup_api/key](https://secure.meetup.com/meetup_api/key)
3. **OpenAI** - [platform.openai.com](https://platform.openai.com)
4. **Apify** - [console.apify.com](https://console.apify.com) (for scraping Luma/Partiful)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/dgupta2003/ai_event_aggregator/issues) page
2. Create a new issue with detailed information
3. Join our discussions for community support

## 🎯 Future Enhancements

- [ ] Natural language query interface
- [ ] Personalized event recommendations
- [ ] Google Calendar integration
- [ ] Mobile app
- [ ] Multi-city support
- [ ] Real-time notifications
- [ ] Event analytics dashboard

---

**Happy coding! 🚀**
