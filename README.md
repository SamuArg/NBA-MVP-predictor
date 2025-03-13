# MVP Predictor

## Overview
MVP Predictor is a machine learning project designed to predict the Most Valuable Player (MVP) in the NBA based on various performance metrics and historical data.

## Features
- Data collection and preprocessing
- Feature engineering
- Model training and evaluation

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/SamuArg/NBA-MVP-predictor.git
    ```
2. Navigate to the backend directory:
    ```sh
    cd mvp-predictor/src/backend
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Create a .env with those this key : MONGOURI and write your own MONGO URI.
5. Run the wsgi.py file to start the backend.

## Features to add
- Get predictions for current season
- Create a website to show current predictions for the season
- Add models and compare them
- Show shap forces to understand what stats impact the most the prediction

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
