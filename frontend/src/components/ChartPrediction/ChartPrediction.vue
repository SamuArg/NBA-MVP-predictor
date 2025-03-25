<template>
  <MvpChart :season="season" />
  <PredictionsList
    :selected-date="selectedDate"
    :players="players"
  />
</template>

<script setup lang="ts">
import type { Prediction } from '@/api/mvps.ts';
import { useChartPrediction } from '@/components/ChartPrediction/useChartPrediction.ts';

const props = defineProps<{ season?: string }>();

const seasonValue = computed(() => props.season);

let selectedDate: ComputedRef<string>, players: Ref<Prediction[]>;

if (seasonValue.value) {
  ({ selectedDate, players } = useChartPrediction(seasonValue.value));
}
</script>
