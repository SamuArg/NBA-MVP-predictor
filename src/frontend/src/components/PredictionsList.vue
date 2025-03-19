<template>
  <v-container>
    <v-list v-if="!loading">
      <v-list-subheader v-if="selectedDate">
        MVP probabilities for {{ selectedDate }}
      </v-list-subheader>
      <v-list-subheader v-else> Latest MVP probabilities </v-list-subheader>
      <PlayerList :players="players" />
    </v-list>
  </v-container>
</template>

<script lang="ts" setup>
import { useMvpPredictions } from "@/composables/useMvpPredictions";
const { players, loading, selectedDate } = useMvpPredictions();
</script>
