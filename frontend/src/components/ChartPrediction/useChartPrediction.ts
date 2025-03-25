import { computed, onMounted, ref, type Ref, watch } from 'vue';
import { getPredictionsSeason, getPredictionsDate, type Prediction } from '@/api/mvps.ts';
import { useAppStore } from '@/stores/app.ts';

export function useChartPrediction(season: string) {
  const players: Ref<Prediction[]> = ref([]);
  const store = useAppStore();
  const selectedDate = computed(() => store.selectedDate);

  const getLastPrediction = async () => {
    const data = await getPredictionsSeason(season);
    if (data) {
      players.value = data[data.length - 1].predictions;
      store.setSelectedDate(data[data.length - 1].date);
    }
  };

  const fetchPredictions = async (date: string) => {
    try {
      const data = await getPredictionsDate(date);
      if (data) players.value = data;
    } catch (error) {
      console.error('Error fetching MVP probabilities:', error);
    }
  };

  onMounted(async () => {
    await getLastPrediction();
  });

  watch(selectedDate, (newDate) => {
    if (newDate) {
      fetchPredictions(newDate);
    } else {
      getLastPrediction();
    }
  });
  return { selectedDate, players };
}
