import { getAllPredictions } from '@/api/mvps.ts';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export function useSideBar() {
  const seasons = ref<{ title: string; value: string }[]>([]);
  const fetchAllPredictions = async () => {
    try {
      const data = await getAllPredictions();
      if (data) return data;
    } catch (error) {
      console.error('Error fetching MVP probabilities:', error);
      return null;
    }
  };

  const getSeasons = async () => {
    const data = await fetchAllPredictions();
    if (data) {
      seasons.value = [
        ...new Map(
          data.map(prediction => [prediction.season, {
            title: String(prediction.season),
            value: String(prediction.season),
          }]),
        ).values(),
      ];
    }
  };

  const router = useRouter();

  const navigateToSeason = (season: string) => {
    router.push({ path: '/historic', query: { season } });
  };

  onMounted(getSeasons);

  return { seasons, navigateToSeason };
}
