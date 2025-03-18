<template>
  <v-container>
    <v-card>
      <v-card-title>MVP Probability Progression</v-card-title>
      <v-card-text>
        <v-progress-circular v-if="loading" indeterminate></v-progress-circular>
        <v-chart
          v-else
          :option="chartOptions"
          @click="onChartClick"
          style="height: 400px"
        ></v-chart>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import VChart from "vue-echarts";
import { useMvpChart } from "@/composables/useMvpChart";
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
  TitleComponent,
} from 'echarts/components';

echarts.use([
  LineChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  TitleComponent,
  CanvasRenderer,
]);


export default defineComponent({
  components: { VChart },
  setup() {
    const { loading, chartOptions, onChartClick } = useMvpChart();
    return { loading, chartOptions, onChartClick };
  },
});
</script>
