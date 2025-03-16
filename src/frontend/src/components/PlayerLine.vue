<template>
  <v-container>
    <v-list>
      <v-list-subheader v-if="date"
        >MVP probabilities for {{ date }}</v-list-subheader
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
import {
  getLatestPredictions,
  getPredictionsDate,
  type Prediction,
} from "../api/mvps";

export default defineComponent({
  props: {
    date: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    const players: Ref<Prediction[]> = ref([]);

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
      if (props.date) {
        await fetchPredictions(props.date);
      } else {
        const data = await getLatestPredictions();
        if (data) {
          players.value = data;
        }
      }
    });
    watch(
      () => props.date,
      (newDate) => {
        if (newDate) {
          fetchPredictions(newDate);
        }
      },
      { immediate: true }
    );

    return { players };
  },
});
</script>
