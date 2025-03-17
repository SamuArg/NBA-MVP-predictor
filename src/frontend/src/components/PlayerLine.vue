<template>
  <v-container>
    <v-list>
      <v-list-subheader v-if="selectedDate"
        >MVP probabilities for {{ selectedDate }}</v-list-subheader
      >
      <v-list-subheader v-else>Latest MVP probabilities</v-list-subheader>
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
import { defineComponent, ref, onMounted, watch, type Ref } from "vue";
import { useAppStore } from "../stores/app";
import {
  getLatestPredictions,
  getPredictionsDate,
  type Prediction,
} from "../api/mvps";

export default defineComponent({
  setup() {
    const players: Ref<Prediction[]> = ref([]);
    const store = useAppStore();
    const selectedDate = computed(() => store.selectedDate);

    const fetchPredictions = async (date: string) => {
      try {
        const data = await getPredictionsDate(date);
        if (data) {
          players.value = data;
        }
      } catch (error) {
        console.error("Error fetching MVP probabilities:", error);
      }
    };

    onMounted(async () => {
      const data = await getLatestPredictions();
      if (data) {
        players.value = data;
      }
    });

    watch(
      selectedDate,
      (newDate) => {
        if (newDate) {
          fetchPredictions(newDate);
        } else {
          getLatestPredictions().then(data => {
            if (data) players.value = data;
          });
        }
      }
    );

    return { players, selectedDate };
  },
});
</script>
