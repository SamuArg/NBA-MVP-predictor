<template>
  <v-list-item
    v-for="(player, index) in players"
    :key="index"
    max-width="500px"
  >
    <v-list-item-title>{{ index + 1 }} - {{ player.player }}</v-list-item-title>
    <v-list-item-subtitle>
      Probability: {{ player.probability.toFixed(2) }}%
    </v-list-item-subtitle>
    <template #append>
      <v-img
        :src="getTeamLogo(player.team)"
        alt="Team Logo"
        width="50"
        height="50"
        contain
      />
    </template>
  </v-list-item>
</template>

<script lang="ts" setup>
import { getTeamLogo } from '@/utils/getTeamLogo';
import type { Prediction } from '@/api/mvps';

defineProps<{ players: Prediction[] }>();
</script>
