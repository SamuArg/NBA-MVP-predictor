<template>
  <div>
    <v-list-item
      v-for="(player, index) in players"
      :key="`${player.player}-${index}`"
      class="py-2"
    >
      <template #prepend>
        <v-avatar
          :color="rankColor(index)"
          variant="tonal"
          size="32"
          class="mr-3"
        >
          <span class="text-caption font-weight-bold">{{ index + 1 }}</span>
        </v-avatar>
      </template>

      <v-list-item-title class="font-weight-medium">
        {{ player.player }}
      </v-list-item-title>

      <v-list-item-subtitle>
        <template v-if="proba">
          Probability: {{ formatPercentage(player.probability) }}
        </template>
        <template v-else>
          MVP share: {{ formatShare(player.probability) }}
        </template>
      </v-list-item-subtitle>

      <v-progress-linear
        v-if="proba && maxProbability > 0"
        :model-value="(player.probability / maxProbability) * 100"
        color="primary"
        height="4"
        rounded
        class="mt-2"
      />

      <template #append>
        <v-img
          :src="getTeamLogo(player.team)"
          :alt="`${player.team} logo`"
          width="42"
          height="42"
          contain
          class="ml-3"
        />
      </template>
    </v-list-item>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { getTeamLogo } from '@/utils/getTeamLogo';
import { formatPercentage, formatShare } from '@/utils/format';
import type { Prediction } from '@/api/mvps';

const props = defineProps<{
  players: Prediction[];
  proba: boolean;
}>();

const maxProbability = computed(() =>
  props.players.reduce(
    (max, player) => Math.max(max, player.probability),
    0,
  ),
);

function rankColor(index: number) {
  if (index === 0) return 'amber';
  if (index === 1) return 'grey-lighten-1';
  if (index === 2) return 'orange-darken-3';
  return 'surface-variant';
}
</script>
