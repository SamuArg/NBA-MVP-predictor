<template>
  <v-container v-if="showChart">
    <v-card>
      <v-card-title>MVP Probability Progression</v-card-title>
      <v-card-text>
        <v-progress-circular
          v-if="loading"
          indeterminate
        />
        <v-chart
          v-else
          :option="chartOptions"
          style="height: 400px"
          @click="(params: any) => onChartClick(params)"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts" setup>
import VChart from 'vue-echarts';
import { useMvpChart } from '@/components/MvpChart/useMvpChart';
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

const props = defineProps<{ season?: string }>();

const seasonValue = computed(() => props.season ?? '2025');

const { showChart, chartOptions, loading, onChartClick } = useMvpChart(seasonValue.value);
</script>
