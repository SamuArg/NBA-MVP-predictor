import { computed, ref, toValue, watch, type MaybeRefOrGetter } from 'vue';
import { useAppStore } from '@/stores/app';
import type { RankingEntry, SeasonPrediction } from '@/api/mvps';
import { ApiError } from '@/api/client';

function errorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong while loading the predictions.';
}

export function useChartPrediction(
  seasonSource: MaybeRefOrGetter<string | number>,
  showRankingSource: MaybeRefOrGetter<boolean> = false,
) {
  const store = useAppStore();

  const season = computed(() => Number(toValue(seasonSource)));
  const showRanking = computed(() => Boolean(toValue(showRankingSource)));

  const seasonData = ref<SeasonPrediction[]>([]);
  const ranking = ref<RankingEntry[]>([]);
  const loading = ref(true);
  const error = ref('');

  const selectedDate = computed(() => store.selectedDate);

  const latestEntry = computed(
    () => seasonData.value[seasonData.value.length - 1],
  );
  const latestDate = computed(() => latestEntry.value?.date ?? '');

  const players = computed(() => {
    if (!selectedDate.value) return latestEntry.value?.predictions ?? [];

    const entry = seasonData.value.find(
      (candidate) => candidate.date === selectedDate.value,
    );
    return entry?.predictions ?? latestEntry.value?.predictions ?? [];
  });

  let requestId = 0;

  async function loadRanking(force = false) {
    if (!showRanking.value || !Number.isInteger(season.value)) return;

    try {
      ranking.value = await store.loadRanking(season.value, force);
    } catch {
      // The predictions remain useful even if the ranking cannot be loaded.
      ranking.value = [];
    }
  }

  async function load(force = false) {
    const currentRequest = ++requestId;

    loading.value = true;
    error.value = '';
    store.setSelectedDate('');

    try {
      const data = await store.loadSeason(season.value, force);
      if (currentRequest !== requestId) return;
      seasonData.value = data;
      await loadRanking(force);
    } catch (loadError) {
      if (currentRequest !== requestId) return;
      seasonData.value = [];
      ranking.value = [];
      error.value = errorMessage(loadError);
    } finally {
      if (currentRequest === requestId) loading.value = false;
    }
  }

  watch(
    season,
    () => {
      void load();
    },
    { immediate: true },
  );

  watch(showRanking, (enabled) => {
    if (enabled) void loadRanking();
  });

  function retry() {
    void load(true);
  }

  function selectDate(date: string) {
    if (!date) {
      store.setSelectedDate('');
      return;
    }

    if (seasonData.value.some((entry) => entry.date === date)) {
      store.setSelectedDate(date);
    }
  }

  return {
    selectedDate,
    latestDate,
    players,
    ranking,
    seasonData,
    loading,
    error,
    retry,
    selectDate,
  };
}
