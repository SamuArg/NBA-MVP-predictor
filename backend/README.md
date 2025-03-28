# NBA MVP Predictor Backend

## Overview
Backend service for the NBA MVP Predictor project. Provides APIs for MVP predictions and historical data using a PyTorch neural network model.

## API Endpoints

### GET /mvps
Get MVP predictions.

Query Parameters:
- `date` (optional): Get predictions for specific date (YYYY-MM-DD)
- `season` (optional): Get all predictions for a season (YYYY)

Returns latest predictions if no parameters provided.

Response format:
```json
[
  {
    "player": "Player Name",
    "probability": 32.63,
    "team": "TEAM"
  }
]
```

### GET /ranking
Get MVP voting results.

Query Parameters:
- `season` (required): Season year (YYYY)

### GET /season
Get current NBA season.

### GET /
Get all historical predictions.

## Project Structure

- `api/` - Flask API endpoints
- `models/` - PyTorch model definition
- `scripts/` - Core functionality
  - `Predict.py` - Prediction pipeline
  - `Scrap.py` - Data scraping from basketball-reference
  - `dailyPredictions.py` - Daily prediction updates
  - `database.py` - MongoDB operations
- `data/` - Raw and processed data
- `notebooks/` - Development notebooks

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Environment variables:
Create `.env` file with:
```
MONGOURI=your_mongodb_connection_string
API_KEY=your_api_key
```

3. Run server:
```bash 
python wsgi.py
```

## Development

- Run tests: `pytest`
- Daily predictions run via GitHub Actions
- Model is retrained yearly with new season data