<template>
  <v-container>
    <v-card>
      <v-card-title>MVP Probability Progression</v-card-title>
      <v-card-text>
        <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
        <v-chart v-else :option="chartOptions" style="height: 400px;"></v-chart>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { MVPResponse } from "../api/mvps";
import { getPredictionsSeason } from "../api/mvps";

use([GridComponent, TooltipComponent, LegendComponent, LineChart, CanvasRenderer]);

export default defineComponent({
  components: { VChart },

  setup() {
    const loading = ref(true);
    const chartOptions = ref({});
    const mvpData = ref<MVPResponse[] | null>(null);

    const transformData = (data: MVPResponse[]) => {
      const dates = data.map(entry => entry.date);
      const players = [...new Set(data.flatMap(entry => entry.predictions.map(p => p.player)))];

      const series = players.map(player => ({
        name: player,
        type: "line",
        data: data.map(entry => {
          const found = entry.predictions.find(p => p.player === player);
          return found ? found.probability : null;
        })
      }));

      return { dates, series, players };
    };

    onMounted(async () => {
      try {
        const rawData = await getPredictionsSeason("2025");
        if (rawData) {
          const { dates, series, players } = transformData(rawData);

          chartOptions.value = {
            tooltip: { trigger: "axis" },
            legend: { data: players },
            xAxis: { type: "category", data: dates },
            yAxis: { type: "value", min: 0, max: 100 },
            series
          };
        }
        loading.value = false;
      } catch (error) {
        console.error("Error fetching MVP probabilities:", error);
        loading.value = false;
      }
    });

    return { loading, chartOptions };
  }
});
</script>
