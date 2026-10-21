# MVP Predictor

## Overview

MVP Predictor is a machine learning project that predicts the NBA's Most
Valuable Player award. It combines historical MVP voting with player and team
statistics, training a model per season and publishing daily predictions for
the current race. Every season back to 1981 can be explored in the frontend.

## Features

- Daily MVP probability predictions for the top 10 candidates
- Interactive probability progression chart; click a date to see that day's rankings
- Home page surfaces official MVP results once voting is available
- Season browser with official MVP voting shares for comparison
- Graceful fallback to the latest available season when the new season has not
  produced predictions yet
- Lightweight season catalogue API and cached frontend requests

## Live demo

You can see a live demo of the project
[here](https://nba-mvp-predictions.netlify.app).

## Project structure

- `backend/` — Flask API, MongoDB access, model pipeline and scrapers
- `frontend/` — Vue 3 + Vuetify single page application
- `.github/workflows/` — daily predictions, MVP voting refresh and tests

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/SamuArg/NBA-MVP-predictor.git
   ```

### Launch the backend

1. Navigate to the backend directory:
   ```sh
   cd NBA-MVP-predictor/backend
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` with `MONGOURI` set to your MongoDB URI.
4. Run the API:
   ```sh
   python wsgi.py
   ```

The API exposes:

- `GET /mvps` (all optional: `?date=YYYY-MM-DD`, `?season=YYYY`)
- `GET /ranking?season=YYYY`
- `GET /season`
- `GET /seasons`
- `GET /health`
- `GET /` (all historical predictions)

Missing dates/seasons return `404` with a JSON error body. See
[`backend/README.md`](backend/README.md) for details.

### Launch the frontend

1. Navigate to the frontend directory:
   ```sh
   cd NBA-MVP-predictor/frontend
   ```
2. Install the required dependencies:
   ```sh
   npm install
   ```
3. Start the dev server:
   ```sh
   npm run dev
   ```

During development, requests go through the Vite proxy (`/api`) to the
deployed backend, avoiding CORS issues. Production builds call the deployed
backend directly. To point the app at another backend, copy `.env.example` to
`.env` and set `VITE_API_URL`.

### Checks

```sh
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run type-check && npm run lint:check && npm run build
```

## Deployment

The frontend is deployed on Netlify and the API on Heroku. The frontend works
against both the previous API (which returned message strings for missing
seasons) and the current API (which returns JSON 404s), so the two services can
be deployed in either order. The `/seasons` endpoint is optional from the
frontend's point of view: when it is unavailable, the app falls back to the
legacy `/` endpoint.

## Features to add

- Show SHAP forces to understand what stats impact the prediction the most
- Update season to season automatically

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE)
file for details.
