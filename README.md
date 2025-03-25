# Flight and Weather Data Collection Application
## Team Nhucaiten - PASS ADY201m

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Last Commit](https://img.shields.io/badge/last%20commit-February%2024%2C%202025-yellow)
![Status](https://img.shields.io/badge/status-active-success)

</div>

## 📑 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [Roles & Contributions](#-roles--contributions)
- [License](#-license)
- [Authors](#-authors)

## 🌟 Overview
The project consists of two main components: **Flight Data Collection** and **Weather Data Collection**. The goal is to build a database of airline ticket prices and weather conditions to help users predict ticket prices and determine optimal booking times.

### 📁 Project Structure
```
Nhucaiten/
├── Project ADY201m/
│  ├── Flight Data Scraper/                # Directory containing flight data collection source code and configuration
│  │   ├── Flight_API/                     # Collect data via SerpAPI
│  |   |   ├── config_flights.txt          # API configuration file and flight route
│  |   |   └── serpapi_tk.py               # Main source code for data collection
│  │   └── Flight_crawl/                   # Collecting data through web scraping
│  |   |   ├── config.txt                  # File cấu hình tuyến bay và thời gian
│  |   |   ├── craw_data_sele_no_ui.py     # Web scraping demo source code
│  |   |   ├── database_manager.py         # Database management module
│  |   |   ├── flight_scraper_ui.py        # Web scraping interface and logic processing module
│  |   |   ├── main.py                     # Program launch file
│  |   |   └── utils.py                    # Module to manage other functions
│  └── Weather Data Scraper/               # Directory containing source code and configuration for collecting weather data
│      ├── config_weather.txt              # API configuration file and city list
│      └── WeatherAPI.py                   # Main source code for weather data collection
├── requirements.txt                       # List of required libraries
└── README.md                              # Project description and manual
```

## ✨ Features

### 🛫 Flight Data Collection
- **Multiple Methods:**
  - API Integration with SerpAPI
  - Automated Web Scraping
- **Advanced Features:**
  - Intuitive Graphical Interface
  - Real-time Telegram Notifications
  - Smart Error Handling
  - Flexible API Key Management
  - CSV/JSON Data Storage

### 🌤️ Weather Data Collection
- **WeatherAPI Integration:**
  - Multidimensional Weather Data
  - Multi-location Support
  - Automatic Translation to Vietnamese
- **User Features:**
  - User-friendly Interface
  - Session Storage
  - CSV Export

## 🚀 Installation

### System Requirements
- Python 3.8 or higher
- Pip package manager

### Installing Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install libraries
pip install -r requirements.txt
```

### API Configuration
1. **SerpAPI Configuration** (`config_flights.txt`):
```ini
[API_KEYS]
your_serp_api_key_1
your_serp_api_key_2

[ROUTES]
HAN-SGN
DAD-HAN
```

2. **Flight Crawler Configuration** (`config.txt`):
```plaintext
HAN-SGN 25/02/2025 3
DAD-DLI 28/04/2025 5
```
Format: `[Departure]-[Arrival] [Flight Date] [Collection Days]`

3. **WeatherAPI Configuration** (`config_weather.txt`):
```ini
[API_KEYS]
your_weather_api_key_1
your_weather_api_key_2

[CITIES]
Ha Noi
Da Nang
```

## 📖 Usage

### Flight Data Collection
```bash
# Using SerpAPI
python Flight_API/serpapi_tk.py

# Or Web Scraping
python Flight_crawl/craw_data_sele_tk.py
```

### Weather Data Collection
```bash
python WeatherAPI.py
```

## 🤝 Contributing
We welcome all contributions! If you want to improve the project:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Authors
- **Nguyen Duc Hoan**
  - GitHub: [Hoann0501](https://github.com/Hoann0501)
  - Email: Nguyenduchoan0501@gmail.com

- **Hoang Ngoc Luu Duc**
  - GitHub: [Iyas123456](https://github.com/Iyas123456)
  - Email: hoangduc.qn122@gmail.com

- **Nguyen Thanh Truong Tuan**
  - GitHub: [OiHuecuata](https://github.com/OiHuecuata)
  - Email: TripleTisworking@gmail.com

- **Huynh Duc Anh**
  - GitHub: [SENULT](https://github.com/SENULT)
  - Email: ducanhhuynh2005@gmail.com

### 🔰 Roles & Contributions

#### Nguyen Thanh Truong Tuan (Team Leader)
- Database management
- Project management and coordination
- User experience optimization

#### Nguyen Duc Hoan
- Lead developer
- System architecture design
- API integration and data processing
- User interaction handling

#### Hoang Ngoc Luu Duc
- Business logic processing
- System performance optimization
- UX/UI design

#### Huynh Duc Anh
- Data analysis
- Reporting and statistics
- System effectiveness evaluation

## 📝 License
This project is developed for research and educational purposes. All content and source code are intellectual property of the authors. Users may reference and use for learning purposes but may not copy or distribute without the authors' permission.

## 📊 Project Statistics

![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=Nhucaiten.FlightWeatherScraper)

## 📞 Contact
If you have any questions or suggestions, please contact us at:
- Email: Nguyenduchoan0501@gmail.com

---
<div align="center">
Made with ❤️ by Nhucaiten Team
</div>
