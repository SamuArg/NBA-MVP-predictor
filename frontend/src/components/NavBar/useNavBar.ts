import { ref } from 'vue';
export function useNavBar() {
  const handleGithubClick = () =>
    window.open('https://github.com/SamuArg/NBA-MVP-predictor', '_blank');
  const drawer = ref(false);
  return { handleGithubClick, drawer };
}
