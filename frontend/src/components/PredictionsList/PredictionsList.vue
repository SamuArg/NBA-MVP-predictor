<template>
  <v-container>
    <v-list>
      <v-list-subheader v-if="selectedDate">
        MVP probabilities for {{ selectedDate }}
      </v-list-subheader>
      <v-list-subheader v-else>
        Latest MVP probabilities
      </v-list-subheader>
      <PlayerList
        :players="players"
        :proba="true"
      />
    </v-list>
  </v-container>
</template>

<script lang="ts" setup>
import type { Prediction } from '@/api/mvps.ts';

defineProps<{ selectedDate: string; players: Prediction[]; }>();
</script>
