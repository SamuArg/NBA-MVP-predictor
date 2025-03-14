# MVP Predictor

## Overview
MVP Predictor is a machine learning project designed to predict the Most Valuable Player (MVP) in the NBA based on various performance metrics and historical data.

## Features
- Data collection and preprocessing
- Feature engineering
- Model training and evaluation

## Live demo
You can see a live demo of the project [here](https://nba-mvp-predictions.netlify.app)

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/SamuArg/NBA-MVP-predictor.git
    ```
### Launch the Backend

1. Navigate to the backend directory:
    ```sh
    cd mvp-predictor/src/backend
    ```
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Create a .env with those this key : MONGOURI and write your own MONGO URI.
4. Run the wsgi.py file to start the backend.

### Launch the frontend

1. Navigate to the frontend directory:
    ```sh
    cd mvp-predictor/src/frontend
    ```
2. Install the required dependencies:
    ```sh
    npm install
    ```
3. If you run your own backend make sure to update the api url.


## Features to add
- Show shap forces to understand what stats impact the most the prediction
- Show for each dates the ranking with probabilities under the table
- Update season to season automatically

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
