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

Missing dates, seasons or rankings return `404` with a JSON body such as:

```json
{ "error": "No predictions available for season 2027.", "season": 2027 }
```

### GET /explain
Get the precomputed SHAP explanation for one player on one date.

Query Parameters:
- `season` (optional): Season year (YYYY)
- `date` (required): Prediction date (YYYY-MM-DD)
- `player` (required): Full player name

The daily prediction job writes these values to MongoDB; the API only reads
them. New predictions include explanations automatically. The backfill workflow
can add them for the final stored date of a completed season (or the current
season's latest date when explicitly requested), and older mid-season dates
without a stored feature snapshot return `404`.

Response format:
```json
{
  "season": 2026,
  "date": "2026-04-30",
  "player": "Shai Gilgeous-Alexander",
  "team": "OKC",
  "probability": 23.85,
  "baseValue": 0.08,
  "outputValue": 0.71,
  "features": [
    {
      "name": "PTS",
      "label": "Points / game",
      "value": 32.0,
      "displayValue": "32.0",
      "contribution": 0.3
    }
  ]
}
```

`probability` is the normalized percentage shown in the ranking. `baseValue`,
`outputValue` and `contribution` describe the model's raw score, so the
contributions add up to `outputValue - baseValue`.

### GET /ranking
Get MVP voting results.

Query Parameters:
- `season` (required): Season year (YYYY)

### GET /season
Get current NBA season.

### GET /seasons
Get the seasons that have predictions, plus the current and latest season.
This is the lightweight alternative to `/` for building season menus.

```json
{
  "current": 2027,
  "latest": 2026,
  "seasons": [
    {
      "season": 2026,
      "predictions": 185,
      "firstDate": "2025-10-24",
      "lastDate": "2026-04-30",
      "hasRanking": true
    }
  ]
}
```

### GET /health
Simple uptime probe that does not touch the database.

### GET /
Get all historical predictions.

## CORS

The production Netlify origin is always allowed. Extra origins can be added
with the `CORS_ORIGINS` environment variable as a comma-separated list. Local
development origins (`localhost:3000` and `localhost:5173`) are included by
default.

## Project Structure

- `api/` - Flask API endpoints
- `models/` - PyTorch model definition
- `scripts/` - Core functionality
  - `Predict.py` - Prediction pipeline
  - `explain.py` - SHAP explanation generation
  - `Scrap.py` - Data scraping from basketball-reference
  - `dailyPredictions.py` - Daily prediction updates
  - `backfill_explanations.py` - Explanation backfill for stored seasons
  - `database.py` - MongoDB operations
- `data/` - Raw and processed data
- `notebooks/` - Development notebooks

## Setup

1. Install dependencies for the API:
```bash
pip install -r requirements.txt
```

The daily prediction job, backfill script and test suite also need SHAP:
```bash
pip install -r requirements-analysis.txt
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

- Run tests: `pytest` (SHAP-specific tests skip when `shap` is not installed)
- Daily predictions run via GitHub Actions
- Backfill explanations with `python -m scripts.backfill_explanations`
  (optionally `--season 2026` or `--dry-run`), or run the
  **Backfill SHAP explanations** workflow
- Model is retrained yearly with new season data

## Deployment

The `backend/` directory is deployed to Heroku automatically by
`.github/workflows/deploy_backend.yml`. It runs after the **Backend Test**
workflow succeeds on `main`, then copies `backend/` into a fresh git repository
and pushes it to the Heroku app (Heroku builds from the repository root).

The app is a container app, so `heroku.yml` tells Heroku to build the image from
`Dockerfile`. The web process uses the Dockerfile `CMD`
(`gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app`).

The app lives at `https://nba-mvp-predictions-0354ab92b6ca.herokuapp.com/`
(Heroku assigned that generated domain to the app named `nba-mvp-predictions`).

The workflow needs a Heroku API key as a repository secret:

```sh
gh secret set HEROKU_API_KEY --repo SamuArg/NBA-MVP-predictor
```

Get the key from the [Heroku account page](https://dashboard.heroku.com/account)
(Account Settings → API Key). Without the secret the deploy step logs a warning
and skips, so pushes never fail on a missing key.
