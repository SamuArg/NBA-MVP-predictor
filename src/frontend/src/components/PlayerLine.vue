<template>
  <v-container>
    <v-list v-if="!loading">
      <v-list-subheader v-if="selectedDate">
        MVP probabilities for {{ selectedDate }}
      </v-list-subheader>
      <v-list-subheader v-else>
        Latest MVP probabilities
      </v-list-subheader>
      <v-list-item v-for="(player, index) in players" :key="index">
        <v-list-item-title>{{ player.player }}</v-list-item-title>
        <v-list-item-subtitle>
          Probability: {{ player.probability.toFixed(2) }}%
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useMvpPredictions } from "@/composables/useMvpPredictions";

export default defineComponent({
  setup() {
    return useMvpPredictions();
  },
});
</script>
