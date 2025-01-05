# News Aggregator

A modern news aggregation system built with Python, featuring real-time scraping, PostgreSQL storage, and a Flask web interface.

## 🚀 Features

- Real-time news scraping with intelligent rate limiting
- PostgreSQL database with optimized schema
- Modern web interface built with Flask and Bootstrap
- Category-based news organization
- Responsive design for all devices
- Error handling and retry mechanisms
- Logging system for monitoring and debugging

## 🛠 Tech Stack

- **Backend**: Python 3.9+
- **Web Framework**: Flask 3.0
- **Database**: PostgreSQL 15
- **Scraping**: BeautifulSoup4, Requests
- **Frontend**: Bootstrap 5.3
- **Container**: Docker & Docker Compose
- **Development**: Poetry (dependency management)

## 📋 Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- PostgreSQL 15 or higher

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/eraybulut34/news-aggregator.git
cd news-aggregator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start PostgreSQL with Docker:
```bash
docker-compose up -d
```

## 🚀 Usage

1. Run the scraper to collect news:
```bash
python scraper.py
```

2. Start the web application:
```bash
python app.py
```

3. Visit `http://localhost:5001` in your browser

## 🏗 Project Structure

```
news-aggregator/
├── app.py              # Flask application
├── scraper.py         # News scraping logic
├── requirements.txt   # Project dependencies
├── docker-compose.yml # Docker configuration
├── README.md         # Project documentation
└── templates/        # HTML templates
    ├── index.html    # Home page template
    └── detail.html   # News detail template
```

## 🔄 Database Schema

```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    url TEXT UNIQUE,
    image_url TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛡 Error Handling

- Automatic retry mechanism for database connections
- Graceful handling of scraping failures
- Rate limiting to prevent server overload
- Comprehensive logging system

## 📝 Logging

The application uses Python's built-in logging system with the following features:
- Log levels: INFO, ERROR
- Timestamp and log level in each message
- Separate logging for scraping and database operations

## 🔒 Security

- SQL injection prevention using parameterized queries
- User-Agent rotation for scraping
- Environment variable based configuration
- No sensitive data in version control

## 🚧 Future Improvements

- [ ] Add user authentication system
- [ ] Implement news search functionality
- [ ] Add API endpoints for mobile applications
- [ ] Implement caching system
- [ ] Add test coverage
- [ ] Set up CI/CD pipeline

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
