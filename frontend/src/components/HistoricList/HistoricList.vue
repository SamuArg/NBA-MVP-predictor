<template>
  <v-list>
    <v-list-subheader>
      Official MVP voting — {{ formatSeasonLabel(season) }}
    </v-list-subheader>

    <PlayerList
      :players="players"
      :proba="false"
    />
  </v-list>
</template>

<script setup lang="ts">
import type { Prediction } from '@/api/mvps.ts';
import { formatSeasonLabel } from '@/utils/format';

defineProps<{ season: string; players: Prediction[]; }>();
</script>
