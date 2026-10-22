<template>
  <v-container v-if="showChart">
    <v-card>
      <v-card-title>MVP Probability Progression</v-card-title>
      <v-card-subtitle v-if="rangeLabel">
        {{ rangeLabel }} · click a date for that day's ranking, or a player's
        line for a SHAP explanation
      </v-card-subtitle>
      <v-card-text>
        <v-chart
          :option="chartOptions"
          :autoresize="true"
          style="height: 400px"
          @click="handleChartClick"
        />

        <div
          class="chart-legend"
          role="list"
          aria-label="Players shown in the chart"
        >
          <span
            v-for="item in legendItems"
            :key="item.name"
            class="chart-legend__item"
            role="listitem"
          >
            <span
              class="chart-legend__dot"
              :style="{ backgroundColor: item.color }"
            />
            {{ item.shortName }}
          </span>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts" setup>
import VChart from 'vue-echarts';
import {
  useMvpChart,
  type ChartSelection,
} from '@/components/MvpChart/useMvpChart';
import type { SeasonPrediction } from '@/api/mvps';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TooltipComponent,
  GridComponent,
  TitleComponent,
  MarkLineComponent,
} from 'echarts/components';

echarts.use([
  LineChart,
  TooltipComponent,
  GridComponent,
  TitleComponent,
  MarkLineComponent,
  CanvasRenderer,
]);

const props = defineProps<{
  data: SeasonPrediction[];
  selectedDate?: string;
}>();

const emit = defineEmits<{
  'select-date': [date: string];
  explain: [selection: ChartSelection];
}>();

const {
  showChart,
  chartOptions,
  rangeLabel,
  legendItems,
  getDateFromEvent,
  getSelectionFromEvent,
} = useMvpChart(
  () => props.data,
  () => props.selectedDate ?? '',
);

function handleChartClick(params: unknown) {
  const selection = getSelectionFromEvent(params);
  if (selection) {
    emit('explain', selection);
    return;
  }

  const date = getDateFromEvent(params);
  if (date) emit('select-date', date);
}
</script>

<style scoped>
.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  padding: 4px 4px 0;
}

.chart-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #cfcfcf;
  font-size: 12px;
  line-height: 1.5;
}

.chart-legend__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: none;
}
</style>
