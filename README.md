# Flight and Weather Data Scraper
# Nhucaiten
# PASS ADY201m

```
Project ADY201m/
├── Flight Data Scraper/            # Directory containing the source code and configuration for flight data collection
│   ├── config_flights.txt          # Configuration file for Flight Data Scraper
│   └── serpapi_tk.py               # Python script using SerpAPI to collect flight data
├── Weather Data Scraper/           # Directory containing the source code and configuration for weather data collection
│   ├── config_weather.txt          # Configuration file for Weather Data Scraper
│   └── WeatherAPI.py               # Python script using WeatherAPI to collect weather data
README.md                           # Instruction and project description file
```

## Description
This project consists of two main components: **Flight Data Scraper** and **Weather Data Scraper**. The goal of the project is to collect information about flights and weather to assist users in predicting ticket prices and the best times to book tickets.

### Key Features
- **Flight Data Scraper**:
  - Retrieves flight information from the SerpApi.
  - Stores flight data in a CSV file.
  - Sends notifications via Telegram regarding the data collection status.

- **Weather Data Scraper**:
  - Retrieves weather information from the WeatherAPI.
  - Translates weather conditions into Vietnamese.
  - Stores weather data in a CSV file.

### Data Results
- **Flight Data**:
  - Airline name
  - Ticket price
  - Flight duration
  - Departure and return times
  - Flight time

- **Weather Data**:
  - Time
  - Day of the year
  - Rainy days
  - Sunny days
  - Cold days
  - Hot days
  - Festival and event days

### Ticket Price Prediction
Based on weather data and flight information, the project will help users predict ticket prices over time and the lead time for booking to achieve the lowest fares.

## Installation
1. **Requirements**:
   - Python 3.x
   - Libraries: `requests`, `tkinter`, `tkcalendar`, `pickle`, `csv`, `json`, `threading`, `queue`

2. **Library Installation**:
   ```bash
   pip install requests tk tkcalendar
   ```

3. **Configuration**:
   - Create a configuration file `config_flights.txt` with the following format:
     ```plaintext
     [API_KEYS]
     <API_KEY_1>
     <API_KEY_2>
     ...
     
     [ROUTES]
     <ORIGIN>-<DESTINATION>
     ...
     ```

   - Create a configuration file `config_weather.txt` with the following format:
     ```plaintext
     [API_KEYS]
     <API_KEY_1>
     <API_KEY_2>
     ...
     
     [CITY]
     <DA NANG>
     ...
     ```

## Usage
- Can be run directly on VSCode.
- Or download the software "Flight Data Scraper.exe" and "Weather Data Scraper.exe" to run.

## Notes
- Ensure that you have valid API keys for both services (SerpApi and WeatherAPI).
- Check the API usage limits to avoid account suspension.

## Author
- Nguyễn Đức Hoàn
- ...
- ...
- ...
- Nguyenduchoan0501@gmail.com
- https://github.com/Hoann0501

## License
This project is developed for research and educational purposes. All content and source code are the intellectual property of the author. Users may refer to and use it for educational purposes, but copying or distributing without the author's permission is not allowed. We encourage contributions and improvements to better serve the community.
