import { ref, watch, onMounted, computed, type Ref } from 'vue';
import { useAppStore } from '@/stores/app';
import {
  getLatestPredictions,
  getPredictionsDate,
  type Prediction,
} from '@/api/mvps';

export function useMvpPredictions() {
  const players: Ref<Prediction[]> = ref([]);
  const store = useAppStore();
  const selectedDate = computed(() => store.selectedDate);
  const loading = computed(() => store.loading);

  const fetchPredictions = async (date: string) => {
    try {
      const data = await getPredictionsDate(date);
      if (data) players.value = data;
    } catch (error) {
      console.error('Error fetching MVP probabilities:', error);
    }
  };

  onMounted(async () => {
    const data = await getLatestPredictions();
    if (data) players.value = data;
  });

  watch(selectedDate, (newDate) => {
    if (newDate) {
      fetchPredictions(newDate);
    } else {
      getLatestPredictions().then((data) => {
        if (data) players.value = data;
      });
    }
  });

  return { loading, players, selectedDate };
}
