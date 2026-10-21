<template>
  <Base>
    <v-container class="py-6">
      <v-progress-circular
        v-if="loading"
        indeterminate
        size="64"
        color="primary"
        class="d-flex mx-auto my-12"
      />

      <v-alert
        v-else-if="error"
        type="error"
        variant="tonal"
        class="my-6"
      >
        <div class="d-flex flex-wrap align-center justify-space-between ga-3">
          <span>{{ error }}</span>
          <v-btn
            color="error"
            variant="outlined"
            size="small"
            @click="load(true)"
          >
            Retry
          </v-btn>
        </div>
      </v-alert>

      <v-alert
        v-else-if="!season"
        type="info"
        variant="tonal"
        class="my-6"
      >
        No predictions are available yet. Check back once the season is
        underway.
      </v-alert>

      <template v-else>
        <v-alert
          v-if="isFallback"
          type="info"
          variant="tonal"
          class="mb-6"
        >
          <strong>
            {{ formatSeasonLabel(currentSeason) }} predictions aren't available
            yet.
          </strong>
          Showing the latest available season,
          {{ formatSeasonLabel(season) }}.
        </v-alert>

        <v-alert
          v-if="rankingWinner"
          type="success"
          variant="tonal"
          icon="mdi-trophy"
          class="mb-6"
        >
          <div class="text-h6">
            {{ formatSeasonLabel(season) }} MVP:
            {{ rankingWinner.player }} ({{ rankingWinner.team }})
          </div>
          <div class="text-body-2">
            The official voting results are shown below alongside the model's
            final predictions.
          </div>
        </v-alert>

        <div class="d-flex flex-wrap align-center ga-3 mb-4">
          <h1 class="text-h4">
            {{ pageTitle }}
          </h1>
          <v-chip
            color="primary"
            variant="tonal"
          >
            {{ formatSeasonLabel(season) }}
          </v-chip>
          <v-chip
            v-if="seasonInfo"
            variant="outlined"
            size="small"
          >
            {{ formatTrackedDays(seasonInfo.predictions) }}
          </v-chip>
          <v-chip
            v-if="seasonInfo?.lastDate"
            variant="outlined"
            size="small"
          >
            Updated {{ formatDate(seasonInfo.lastDate) }}
          </v-chip>
        </div>

        <ChartPrediction
          :season="season"
          :show-ranking="true"
          :final="Boolean(rankingWinner)"
        />
      </template>
    </v-container>
  </Base>
</template>

<script lang="ts" setup>
import Base from '@/layouts/Base.vue';
import { useAppStore } from '@/stores/app';
import { formatDate, formatSeasonLabel, formatTrackedDays } from '@/utils/format';
import { ApiError } from '@/api/client';
import type { RankingEntry, SeasonInfo } from '@/api/mvps';
import { computed, onMounted, ref } from 'vue';

const store = useAppStore();

const loading = ref(true);
const error = ref('');
const currentSeason = ref<number | null>(null);
const season = ref<number | null>(null);
const availableSeasons = ref<SeasonInfo[]>([]);
const officialRanking = ref<RankingEntry[]>([]);

const isFallback = computed(
  () =>
    currentSeason.value !== null &&
    season.value !== null &&
    currentSeason.value !== season.value,
);

const rankingWinner = computed(() => officialRanking.value[0] ?? null);

const pageTitle = computed(() => {
  if (rankingWinner.value) return 'Final MVP results';
  return isFallback.value ? 'Latest MVP race' : 'Current MVP race';
});

const seasonInfo = computed(() =>
  availableSeasons.value.find((entry) => entry.season === season.value),
);

function messageFor(loadError: unknown) {
  if (loadError instanceof ApiError) return loadError.message;
  return 'Unable to load the MVP predictions right now.';
}

async function load(force = false) {
  loading.value = true;
  error.value = '';

  officialRanking.value = [];

  try {
    const catalogue = await store.loadSeasons(force);
    availableSeasons.value = catalogue.seasons;
    currentSeason.value = catalogue.current;

    const seasonsWithData = catalogue.seasons.map((entry) => entry.season);
    if (seasonsWithData.length === 0) {
      season.value = null;
      return;
    }

    const latest = catalogue.latest ?? Math.max(...seasonsWithData);
    const selectedSeason =
      catalogue.current !== null && seasonsWithData.includes(catalogue.current)
        ? catalogue.current
        : latest;
    season.value = selectedSeason;

    try {
      officialRanking.value = await store.loadRanking(selectedSeason, force);
    } catch {
      // Keep the predictions visible if the official results cannot load.
      officialRanking.value = [];
    }
  } catch (loadError) {
    error.value = messageFor(loadError);
    season.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(() => load());
</script>
