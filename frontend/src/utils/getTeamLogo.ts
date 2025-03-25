export const getTeamLogo = (team: string) => {
  return new URL(`../assets/nba_logos/${team}.png`, import.meta.url).href;
};
