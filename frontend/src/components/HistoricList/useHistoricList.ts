import { useAppStore } from '@/stores/app.ts';
import { computed } from 'vue';

export function useHistoricList() {
  const store = useAppStore();
  const loading = computed(() => store.loading);
  return { loading };
}
