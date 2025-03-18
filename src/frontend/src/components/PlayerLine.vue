<template>
  <v-container>
    <v-list v-if="!loading">
      <v-list-subheader v-if="selectedDate">
        MVP probabilities for {{ selectedDate }}
      </v-list-subheader>
      <v-list-subheader v-else>
        Latest MVP probabilities
      </v-list-subheader>
      <v-list-item v-for="(player, index) in players" :key="index" max-width="500px">

        <v-list-item-title>{{index + 1}} - {{ player.player }}</v-list-item-title>
        <v-list-item-subtitle>
          Probability: {{ player.probability.toFixed(2) }}%
        </v-list-item-subtitle>
        <template v-slot:append>
          <v-img
            :src="getTeamLogo(player.team)"
            alt="Team Logo"
            width="50"
            height="50"
            contain
          ></v-img>
        </template>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useMvpPredictions } from "@/composables/useMvpPredictions";
import { getTeamLogo } from "@/utils/getTeamLogo";

export default defineComponent({
  methods: {getTeamLogo},
  setup() {
    return useMvpPredictions();
  },
});
</script>
