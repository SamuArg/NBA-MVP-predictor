<template>
  <v-container>
    <v-list>
      <v-list-subheader>Official MVP ranking for season {{ season }}</v-list-subheader>
      <PlayerList
        :players="players"
        :proba="false"
      />
    </v-list>
  </v-container>
</template>

<script setup lang="ts">
import type { Prediction } from '@/api/mvps.ts';

defineProps<{ season: string; players: Prediction[]; }>();
</script>
