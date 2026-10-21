import { ref } from 'vue';
import { defineStore } from 'pinia';
import {
  getSeasons,
  getSeasonPredictions,
  getMvpRanking,
  type RankingEntry,
  type SeasonCatalogue,
  type SeasonPrediction,
} from '@/api/mvps';

const CACHE_TTL_MS = 5 * 60 * 1000;

interface CacheEntry<T> {
  data: T;
  loadedAt: number;
}

function isFresh<T>(entry: CacheEntry<T> | undefined): entry is CacheEntry<T> {
  return entry !== undefined && Date.now() - entry.loadedAt < CACHE_TTL_MS;
}

export const useAppStore = defineStore('app', () => {
  const selectedDate = ref('');

  const seasons = ref<SeasonCatalogue | null>(null);
  const seasonsLoadedAt = ref(0);
  const seasonCache = ref<Record<number, CacheEntry<SeasonPrediction[]>>>({});
  const rankingCache = ref<Record<number, CacheEntry<RankingEntry[]>>>({});

  let seasonsRequest: Promise<SeasonCatalogue> | null = null;

  function setSelectedDate(date: string) {
    selectedDate.value = date;
  }

  /**
   * Load the list of seasons with predictions, requesting it at most once
   * per session (unless forced or expired).
   */
  async function loadSeasons(force = false): Promise<SeasonCatalogue> {
    const cachedIsFresh =
      seasons.value !== null &&
      Date.now() - seasonsLoadedAt.value < CACHE_TTL_MS;

    if (!force && cachedIsFresh) return seasons.value as SeasonCatalogue;
    if (!force && seasonsRequest) return seasonsRequest;

    seasonsRequest = getSeasons()
      .then((catalogue) => {
        seasons.value = catalogue;
        seasonsLoadedAt.value = Date.now();
        return catalogue;
      })
      .finally(() => {
        seasonsRequest = null;
      });

    return seasonsRequest;
  }

  async function loadSeason(
    season: number,
    force = false,
  ): Promise<SeasonPrediction[]> {
    const cached = seasonCache.value[season];
    if (!force && isFresh(cached)) return cached.data;

    const data = await getSeasonPredictions(season);
    seasonCache.value = {
      ...seasonCache.value,
      [season]: { data, loadedAt: Date.now() },
    };
    return data;
  }

  async function loadRanking(
    season: number,
    force = false,
  ): Promise<RankingEntry[]> {
    const cached = rankingCache.value[season];
    if (!force && isFresh(cached)) return cached.data;

    const data = await getMvpRanking(season);
    rankingCache.value = {
      ...rankingCache.value,
      [season]: { data, loadedAt: Date.now() },
    };
    return data;
  }

  return {
    selectedDate,
    seasons,
    seasonCache,
    rankingCache,
    setSelectedDate,
    loadSeasons,
    loadSeason,
    loadRanking,
  };
});
