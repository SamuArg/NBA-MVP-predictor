<template>
  <MvpChart :season="season" />
  <v-container>
    <v-row>
      <v-col
        col="6"
      >
        <PredictionsList
          :selected-date="selectedDate"
          :players="players"
        />
      </v-col>
      <v-col
        v-if="showRanking && ranking.length > 1"
        col="6"
      >
        <HistoricList

          :players="ranking"
          :season="season"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { Prediction } from '@/api/mvps.ts';
import { useChartPrediction } from '@/components/ChartPrediction/useChartPrediction.ts';
import { computed } from 'vue';

const props = defineProps<{ season: string; showRanking: boolean }>();

const seasonValue = computed(() => props.season);
const showRankingValue = computed(() => props.showRanking);

let selectedDate: ComputedRef<string>, players: Ref<Prediction[]>, ranking: Ref<Prediction[]>;

if (seasonValue.value) {
  ({
    selectedDate,
    players,
    ranking,
  } = useChartPrediction(seasonValue.value, showRankingValue.value));
}
</script>
