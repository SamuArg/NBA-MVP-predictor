const URL = 'https://nba-mvp-predictor.onrender.com/';

//const URL = 'http://localhost:5000/';


export interface Prediction {
  player: string;
  probability: number;
  team: string;
}

export interface MVPResponse {
  date: string;
  predictions: Prediction[];
  season: number;
}

export const getPredictionsSeason = async (
  season: string,
): Promise<MVPResponse[] | null> => {
  try {
    const response = await fetch(
      `${URL}mvps?season=${season}`,
    );

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching MVP probabilities:', error);
    return null;
  }
};

export const getPredictionsDate = async (
  date: string,
): Promise<Prediction[] | null> => {
  try {
    const response = await fetch(
      `${URL}mvps?date=${date}`,
    );

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching MVP probabilities:', error);
    return null;
  }
};

export const getLatestPredictions = async (): Promise<Prediction[] | null> => {
  try {
    const response = await fetch(`${URL}mvps`);
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching MVP probabilities:', error);
    return null;
  }
};

export const getAllPredictions = async (): Promise<MVPResponse[] | null> => {
  try {
    const response = await fetch(URL);
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching Predictions', error);
    return null;
  }
};

export const getMvpRanking = async (season: string): Promise<Prediction[] | null> => {
  try {
    const response = await fetch(`${URL}ranking?season=${season}`);
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching ranking', error);
    return null;
  }
};

export const getSeason = async (): Promise<string | null> => {
  try {
    const response = await fetch(`${URL}season`);
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.log('Error fetching season', error);
    return null;
  }
};
