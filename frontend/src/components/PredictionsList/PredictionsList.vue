<template>
  <v-list>
    <v-list-subheader>
      <template v-if="selectedDate">
        Predictions for {{ formatDate(selectedDate) }}
      </template>
      <template v-else-if="final">
        Final model predictions<template v-if="latestDate">
          ({{ formatDate(latestDate) }})
        </template>
      </template>
      <template v-else>
        Latest predictions<template v-if="latestDate">
          ({{ formatDate(latestDate) }})
        </template>
      </template>
    </v-list-subheader>

    <PlayerList
      :players="players"
      :proba="true"
    />
  </v-list>
</template>

<script lang="ts" setup>
import type { Prediction } from '@/api/mvps.ts';
import { formatDate } from '@/utils/format';

withDefaults(
  defineProps<{
    selectedDate: string;
    players: Prediction[];
    latestDate?: string;
    final?: boolean;
  }>(),
  {
    latestDate: '',
    final: false,
  },
);
</script>
