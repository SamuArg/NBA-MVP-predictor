const logos = import.meta.glob('../assets/nba_logos/*.png', {
  eager: true,
  import: 'default',
}) as Record<string, string>;

const fallbackLogo = new URL('../assets/logo.svg', import.meta.url).href;

export const getTeamLogo = (team: string) => {
  if (!team) return fallbackLogo;
  return logos[`../assets/nba_logos/${team}.png`] ?? fallbackLogo;
};
