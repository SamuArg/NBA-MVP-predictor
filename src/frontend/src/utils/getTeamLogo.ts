export const getTeamLogo = (team: string) => {
  try {
    return new URL(`../assets/nba_logos/${team}.png`, import.meta.url).href;
  } catch {
    return "https://via.placeholder.com/50"; // Fallback image
  }
};
