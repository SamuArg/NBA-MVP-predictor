import { computed } from 'vue';
import { useAppStore } from '@/stores/app';

export function useMvpPredictions() {
  const store = useAppStore();
  const loading = computed(() => store.loading);

  return { loading };
}
