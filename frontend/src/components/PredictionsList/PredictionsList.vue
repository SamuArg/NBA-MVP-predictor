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
      clickable
      @select="handleSelect"
    />
  </v-list>
</template>

<script lang="ts" setup>
import type { Prediction } from '@/api/mvps.ts';
import { formatDate } from '@/utils/format';

const props = withDefaults(
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

const emit = defineEmits<{
  explain: [
    target: { date: string; player: string; probability: number },
  ];
}>();

function handleSelect(player: Prediction) {
  const date = props.selectedDate || props.latestDate;
  if (!date) return;

  emit('explain', {
    date,
    player: player.player,
    probability: player.probability,
  });
}
</script>
