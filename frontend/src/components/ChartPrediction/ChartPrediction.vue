<template>
  <div>
    <v-progress-circular
      v-if="loading"
      indeterminate
      size="64"
      color="primary"
      class="d-flex mx-auto my-10"
    />

    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="my-6"
    >
      <div
        class="d-flex flex-wrap align-center justify-space-between ga-3"
      >
        <span>{{ error }}</span>
        <v-btn
          color="error"
          variant="outlined"
          size="small"
          @click="retry"
        >
          Retry
        </v-btn>
      </div>
    </v-alert>

    <template v-else>
      <v-container
        v-if="seasonData.length === 0"
        class="py-10 text-center"
      >
        <v-icon
          icon="mdi-basketball"
          size="48"
          class="mb-4 text-medium-emphasis"
        />
        <p class="text-body-1 mb-4">
          No predictions are available for the
          {{ formatSeasonLabel(season) }} season yet.
        </p>
        <slot name="empty" />
      </v-container>

      <template v-else>
        <MvpChart
          :data="seasonData"
          :selected-date="selectedDate"
          @select-date="selectDate"
          @explain="openExplanation"
        />

        <v-container>
          <v-row>
            <v-col
              cols="12"
              :md="showRanking && ranking.length > 0 ? 6 : 12"
            >
              <PredictionsList
                :selected-date="selectedDate"
                :players="players"
                :latest-date="latestDate"
                :final="final"
                @explain="openExplanation"
              />
            </v-col>
            <v-col
              v-if="showRanking && ranking.length > 0"
              cols="12"
              md="6"
            >
              <HistoricList
                :players="ranking"
                :season="String(season)"
              />
            </v-col>
          </v-row>
        </v-container>
      </template>
    </template>

    <PlayerExplanation
      v-model="explanationOpen"
      :season="Number(season)"
      :date="explanationTarget?.date ?? ''"
      :player="explanationTarget?.player ?? ''"
      :probability="explanationTarget?.probability ?? 0"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useChartPrediction } from '@/components/ChartPrediction/useChartPrediction.ts';
import { formatSeasonLabel } from '@/utils/format';

const props = withDefaults(
  defineProps<{
    season: string | number;
    showRanking?: boolean;
    final?: boolean;
  }>(),
  {
    showRanking: false,
    final: false,
  },
);

const {
  selectedDate,
  latestDate,
  players,
  ranking,
  seasonData,
  loading,
  error,
  retry,
  selectDate,
} = useChartPrediction(
  () => props.season,
  () => props.showRanking,
);

interface ExplanationTarget {
  date: string;
  player: string;
  probability: number;
}

const explanationOpen = ref(false);
const explanationTarget = ref<ExplanationTarget | null>(null);

function openExplanation(target: ExplanationTarget) {
  selectDate(target.date);
  explanationTarget.value = target;
  explanationOpen.value = true;
}
</script>
