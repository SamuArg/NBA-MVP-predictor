export interface Prediction {
    player: string;
    probability: number;
  }
  
  export interface MVPResponse {
    date: string;
    predictions: Prediction[];
  }
  
  export const getPredictionsSeason = async (season: string): Promise<MVPResponse[] | null> => {
    try {
      const response = await fetch(`https://nba-mvp-predictor.onrender.com/mvps?season=${season}`);
  
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
  
      const data: MVPResponse[] = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching MVP probabilities:", error);
      return null;
    }
  };
  