export function useNavBar() {
  const handleGithubClick = () =>
    window.open("https://github.com/SamuArg/NBA-MVP-predictor", "_blank");

  return { handleGithubClick };
}
