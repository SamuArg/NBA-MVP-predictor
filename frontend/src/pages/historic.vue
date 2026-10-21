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
            @click="load"
          >
            Retry
          </v-btn>
        </div>
      </v-alert>

      <v-alert
        v-else-if="notFound"
        type="warning"
        variant="tonal"
        class="my-6"
      >
        <div class="d-flex flex-column ga-3">
          <span>
            Season {{ requestedSeason ?? '—' }} isn't available.
            <template v-if="latestSeason">
              The latest season with predictions is
              {{ formatSeasonLabel(latestSeason) }}.
            </template>
          </span>
          <div class="d-flex flex-wrap ga-2">
            <v-btn
              v-if="latestSeason"
              color="warning"
              variant="flat"
              @click="goToSeason(latestSeason)"
            >
              View {{ formatSeasonLabel(latestSeason) }}
            </v-btn>
            <v-btn
              to="/"
              variant="outlined"
            >
              Current race
            </v-btn>
          </div>
        </div>
      </v-alert>

      <template v-else-if="season">
        <div
          class="d-flex flex-wrap align-center justify-space-between ga-2 mb-4"
        >
          <div class="d-flex align-center ga-2">
            <v-btn
              icon="mdi-chevron-left"
              variant="text"
              :disabled="!previousSeason"
              :aria-label="
                previousSeason
                  ? `View ${formatSeasonLabel(previousSeason)}`
                  : 'No previous season'
              "
              @click="goToSeason(previousSeason)"
            />
            <div>
              <h1 class="text-h4">
                Season {{ formatSeasonLabel(season) }}
              </h1>
              <p
                v-if="seasonInfo"
                class="text-body-2 text-medium-emphasis mb-0"
              >
                {{ formatTrackedDays(seasonInfo.predictions) }}
                <template v-if="seasonInfo.firstDate">
                  · {{ formatDate(seasonInfo.firstDate) }} –
                  {{ formatDate(seasonInfo.lastDate) }}
                </template>
              </p>
            </div>
            <v-btn
              icon="mdi-chevron-right"
              variant="text"
              :disabled="!nextSeason"
              :aria-label="
                nextSeason
                  ? `View ${formatSeasonLabel(nextSeason)}`
                  : 'No next season'
              "
              @click="goToSeason(nextSeason)"
            />
          </div>

          <v-btn
            to="/"
            variant="outlined"
            prepend-icon="mdi-basketball"
          >
            Current race
          </v-btn>
        </div>

        <ChartPrediction
          :season="season"
          :show-ranking="true"
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
import type { SeasonInfo } from '@/api/mvps';
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const store = useAppStore();

const loading = ref(true);
const error = ref('');
const notFound = ref(false);
const season = ref<number | null>(null);
const availableSeasons = ref<SeasonInfo[]>([]);

const requestedSeason = computed(() => {
  const raw = route.query.season;
  const value = Number(Array.isArray(raw) ? raw[0] : raw);
  return Number.isFinite(value) && value > 0 ? value : null;
});

const sortedSeasons = computed(() =>
  [...availableSeasons.value].sort((a, b) => a.season - b.season),
);

const latestSeason = computed(
  () => sortedSeasons.value[sortedSeasons.value.length - 1]?.season ?? null,
);

const seasonInfo = computed(() =>
  availableSeasons.value.find((entry) => entry.season === season.value),
);

const seasonIndex = computed(() =>
  sortedSeasons.value.findIndex((entry) => entry.season === season.value),
);

const previousSeason = computed(() => {
  const index = seasonIndex.value;
  return index > 0 ? sortedSeasons.value[index - 1].season : null;
});

const nextSeason = computed(() => {
  const index = seasonIndex.value;
  return index >= 0 && index < sortedSeasons.value.length - 1
    ? sortedSeasons.value[index + 1].season
    : null;
});

function messageFor(loadError: unknown) {
  if (loadError instanceof ApiError) return loadError.message;
  return 'Unable to load this season right now.';
}

let requestId = 0;

async function load() {
  const currentRequest = ++requestId;

  loading.value = true;
  error.value = '';
  notFound.value = false;

  try {
    const catalogue = await store.loadSeasons();
    if (currentRequest !== requestId) return;

    availableSeasons.value = catalogue.seasons;

    const requested = requestedSeason.value;
    if (requested === null) {
      season.value = latestSeason.value;
      notFound.value = season.value === null;

      // Keep the URL shareable by pointing it at the season being shown.
      if (season.value !== null) {
        void router.replace({
          path: '/historic',
          query: { season: String(season.value) },
        });
      }
      return;
    }

    const exists = catalogue.seasons.some(
      (entry) => entry.season === requested,
    );

    if (!exists) {
      season.value = null;
      notFound.value = true;
      return;
    }

    season.value = requested;
  } catch (loadError) {
    if (currentRequest !== requestId) return;
    error.value = messageFor(loadError);
    season.value = null;
  } finally {
    if (currentRequest === requestId) loading.value = false;
  }
}

function goToSeason(target: number | null) {
  if (target === null) return;
  void router.push({ path: '/historic', query: { season: String(target) } });
}

watch(requestedSeason, load, { immediate: true });
</script>
