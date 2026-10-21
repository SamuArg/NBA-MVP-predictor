import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/stores/app';
import { ApiError } from '@/api/client';

export function useSideBar() {
  const store = useAppStore();
  const route = useRoute();

  const loading = ref(store.seasons === null);
  const error = ref('');

  const seasons = computed(() => store.seasons?.seasons ?? []);

  const activeSeason = computed(() => {
    if (route.path !== '/historic') return null;
    const raw = route.query.season;
    const value = Number(Array.isArray(raw) ? raw[0] : raw);
    return Number.isFinite(value) && value > 0 ? value : null;
  });

  async function loadSeasons() {
    if (store.seasons) return;

    loading.value = true;
    error.value = '';
    try {
      await store.loadSeasons();
    } catch (loadError) {
      error.value =
        loadError instanceof ApiError
          ? loadError.message
          : 'Unable to load seasons.';
    } finally {
      loading.value = false;
    }
  }

  onMounted(loadSeasons);

  return { seasons, loading, error, activeSeason };
}
