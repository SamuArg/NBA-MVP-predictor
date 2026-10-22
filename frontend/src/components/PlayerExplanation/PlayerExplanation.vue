<template>
  <v-dialog
    :model-value="modelValue"
    max-width="900"
    scrollable
    @update:model-value="handleModelValue"
  >
    <v-card>
      <v-card-title class="d-flex flex-wrap align-center ga-3 py-4">
        <v-img
          v-if="team"
          :src="getTeamLogo(team)"
          :alt="`${team} logo`"
          width="44"
          height="44"
          contain
        />

        <div class="min-w-0">
          <div class="text-h6">
            {{ player }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ team || '—' }} · {{ formatDate(date) }}
          </div>
        </div>

        <v-spacer />

        <v-chip
          color="primary"
          variant="tonal"
        >
          {{ formatPercentage(displayProbability) }}
        </v-chip>

        <v-btn
          icon="mdi-close"
          variant="text"
          aria-label="Close explanation"
          @click="close"
        />
      </v-card-title>

      <v-divider />

      <v-card-text class="py-5">
        <div
          v-if="loading"
          class="d-flex justify-center py-10"
        >
          <v-progress-circular
            indeterminate
            color="primary"
            size="48"
          />
        </div>

        <v-alert
          v-else-if="error"
          type="info"
          variant="tonal"
        >
          {{ error }}
        </v-alert>

        <template v-else-if="explanation">
          <ShapForcePlot :explanation="explanation" />

          <v-divider class="my-5" />

          <div class="text-subtitle-2 mb-2">
            Biggest drivers
          </div>

          <v-table
            density="compact"
            class="explanation-table"
          >
            <thead>
              <tr>
                <th>Feature</th>
                <th>Value</th>
                <th class="text-right">
                  Impact
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="feature in topFeatures"
                :key="feature.name"
              >
                <td>{{ feature.label }}</td>
                <td class="text-medium-emphasis">
                  {{ feature.displayValue }}
                </td>
                <td
                  class="text-right font-weight-medium"
                  :class="impactClass(feature.contribution)"
                >
                  {{ formatImpact(feature.contribution) }}
                </td>
              </tr>
            </tbody>
          </v-table>

          <p class="text-caption text-medium-emphasis mt-4 mb-0">
            SHAP explains the model's raw score. The probability shown above is
            normalized across the top 10 candidates, so it is not additive in
            these contributions. The bar shows the ten largest drivers; smaller
            features are combined into "Other features." Red pushes the raw
            score up; blue pushes it down.
          </p>
        </template>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import { useAppStore } from '@/stores/app';
import { ApiError } from '@/api/client';
import type {
  FeatureContribution,
  PlayerExplanation,
} from '@/api/mvps';
import { formatDate, formatPercentage } from '@/utils/format';
import { getTeamLogo } from '@/utils/getTeamLogo';

const props = defineProps<{
  modelValue: boolean;
  season: number;
  date: string;
  player: string;
  probability: number;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

const store = useAppStore();

const explanation = ref<PlayerExplanation | null>(null);
const loading = ref(false);
const error = ref('');
let requestId = 0;

const team = computed(() => explanation.value?.team ?? '');
const displayProbability = computed(
  () => explanation.value?.probability ?? props.probability,
);

const topFeatures = computed<FeatureContribution[]>(() =>
  [...(explanation.value?.features ?? [])]
    .sort(
      (left, right) =>
        Math.abs(right.contribution) - Math.abs(left.contribution),
    )
    .slice(0, 10),
);

function formatImpact(value: number) {
  if (!Number.isFinite(value)) return '—';
  const sign = value >= 0 ? '+' : '−';
  return `${sign}${Math.abs(value).toFixed(3)}`;
}

function impactClass(value: number) {
  return value >= 0 ? 'impact-up' : 'impact-down';
}

async function load() {
  if (!props.modelValue) return;

  const currentRequest = ++requestId;
  loading.value = true;
  error.value = '';
  explanation.value = null;

  try {
    const data = await store.loadExplanation(
      props.season,
      props.date,
      props.player,
    );
    if (currentRequest !== requestId) return;

    if (!data) {
      error.value =
        'SHAP explanations are not available for this date. Older ' +
        'predictions were stored without a feature snapshot.';
      return;
    }

    explanation.value = data;
  } catch (loadError) {
    if (currentRequest !== requestId) return;

    error.value =
      loadError instanceof ApiError
        ? loadError.message
        : 'Unable to load the explanation right now.';
  } finally {
    if (currentRequest === requestId) loading.value = false;
  }
}

function handleModelValue(value: boolean) {
  emit('update:modelValue', value);
}

function close() {
  emit('update:modelValue', false);
}

watch(
  () => [props.modelValue, props.season, props.date, props.player] as const,
  () => {
    if (props.modelValue) void load();
  },
  { immediate: true },
);
</script>

<style scoped>
.min-w-0 {
  min-width: 0;
}

.explanation-table {
  background: transparent;
}

.explanation-table :deep(th) {
  font-size: 12px;
  color: #9e9e9e;
  font-weight: 500;
}

.explanation-table :deep(td) {
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.impact-up {
  color: #ef5350;
}

.impact-down {
  color: #64b5f6;
}
</style>
