import { computed, toValue, type MaybeRefOrGetter } from 'vue';
import type { EChartsOption } from 'echarts';
import type { SeasonPrediction } from '@/api/mvps';
import { formatDate } from '@/utils/format';

interface TooltipParams {
  marker: string;
  seriesName: string;
  value: number | null;
}

export interface ChartSelection {
  date: string;
  player: string;
  probability: number;
}

const AXIS_LABEL_COLOR = '#b8b8b8';
const SPLIT_LINE_COLOR = 'rgba(255, 255, 255, 0.08)';
const SERIES_COLORS = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
  '#3ba272',
  '#fc8452',
  '#9a60b4',
  '#ea7ccc',
  '#c4a7e7',
];

function shortPlayerName(name: string) {
  const parts = name.trim().split(/\s+/);
  if (parts.length <= 1) return name;

  const suffix = parts[parts.length - 1].toLowerCase();
  if (['jr.', 'sr.', 'ii', 'iii', 'iv'].includes(suffix) && parts.length >= 3) {
    return parts[parts.length - 2];
  }

  return parts[parts.length - 1];
}

export function useMvpChart(
  dataSource: MaybeRefOrGetter<SeasonPrediction[]>,
  selectedDateSource: MaybeRefOrGetter<string> = '',
) {
  const data = computed(() => toValue(dataSource));
  const selectedDate = computed(() => toValue(selectedDateSource));

  const showChart = computed(() => data.value.length >= 2);

  const rangeLabel = computed(() => {
    const first = data.value[0]?.date;
    const last = data.value[data.value.length - 1]?.date;
    if (!first || !last) return '';
    return `${formatDate(first)} – ${formatDate(last)}`;
  });

  const chartPlayers = computed(() => {
    const lastEntry = data.value[data.value.length - 1];

    return [...(lastEntry?.predictions ?? [])]
      .sort((a, b) => b.probability - a.probability)
      .slice(0, 10)
      .map((entry, index) => ({
        name: entry.player,
        shortName: shortPlayerName(entry.player),
        color: SERIES_COLORS[index % SERIES_COLORS.length],
      }));
  });

  const chartOptions = computed<EChartsOption>(() => {
    const series = chartPlayers.value.map((player) => ({
      name: player.name,
      type: 'line' as const,
      smooth: true,
      showSymbol: false,
      symbol: 'circle',
      symbolSize: 4,
      connectNulls: true,
      triggerEvent: true,
      sampling: 'lttb' as const,
      itemStyle: { color: player.color },
      lineStyle: { color: player.color },
      emphasis: { focus: 'series' as const },
      data: data.value.map(
        (entry) =>
          entry.predictions.find(
            (prediction) => prediction.player === player.name,
          )?.probability ?? null,
      ),
    }));

    if (series.length > 0 && selectedDate.value) {
      Object.assign(series[0], {
        markLine: {
          symbol: 'none',
          silent: true,
          label: { show: false },
          lineStyle: {
            color: '#f5a623',
            type: 'dashed' as const,
            width: 1,
          },
          data: [{ xAxis: selectedDate.value }],
        },
      });
    }

    return {
      animationDuration: 300,
      textStyle: { color: AXIS_LABEL_COLOR },
      grid: {
        left: 16,
        right: 24,
        top: 24,
        bottom: 16,
        containLabel: true,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(24, 24, 24, 0.96)',
        borderColor: '#444',
        textStyle: { color: '#ffffff' },
        axisPointer: { type: 'line' },
        formatter: (params: unknown) => {
          const entries = (Array.isArray(params) ? params : [params]) as
            TooltipParams[];

          return entries
            .filter((entry) => typeof entry.value === 'number')
            .sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
            .map(
              (entry) =>
                `${entry.marker} ${entry.seriesName}: ${(
                  entry.value ?? 0
                ).toFixed(2)}%`,
            )
            .join('<br/>');
        },
      },
      xAxis: {
        type: 'category',
        data: data.value.map((entry) => entry.date),
        axisPointer: { show: true, snap: true },
        axisLabel: {
          color: AXIS_LABEL_COLOR,
          formatter: (value: string) => value.slice(5),
        },
        axisLine: { lineStyle: { color: '#555' } },
        triggerEvent: true,
      },
      yAxis: {
        type: 'value',
        min: 0,
        axisLabel: {
          color: AXIS_LABEL_COLOR,
          formatter: '{value}%',
        },
        splitLine: { lineStyle: { color: SPLIT_LINE_COLOR } },
      },
      series,
    } as EChartsOption;
  });

  function getDateFromEvent(params: unknown): string | null {
    if (typeof params !== 'object' || params === null) return null;

    const event = params as { componentType?: string; value?: unknown };
    if (event.componentType !== 'xAxis') return null;

    const value = String(event.value ?? '');
    return value.length > 0 ? value : null;
  }

  function getSelectionFromEvent(params: unknown): ChartSelection | null {
    if (typeof params !== 'object' || params === null) return null;

    const event = params as {
      componentType?: string;
      dataIndex?: unknown;
      name?: unknown;
      seriesName?: unknown;
      value?: unknown;
    };
    if (event.componentType !== 'series') return null;

    const player = String(event.seriesName ?? '');
    if (!player) return null;

    const dataIndex =
      typeof event.dataIndex === 'number' ? event.dataIndex : Number.NaN;
    const entry = Number.isInteger(dataIndex)
      ? data.value[dataIndex]
      : undefined;
    const date = entry?.date ?? String(event.name ?? '');
    if (!date) return null;

    let probability =
      typeof event.value === 'number' ? event.value : Number.NaN;
    if (!Number.isFinite(probability)) {
      probability =
        entry?.predictions.find((prediction) => prediction.player === player)
          ?.probability ?? Number.NaN;
    }
    if (!Number.isFinite(probability)) return null;

    return { date, player, probability };
  }

  return {
    showChart,
    chartOptions,
    rangeLabel,
    legendItems: chartPlayers,
    getDateFromEvent,
    getSelectionFromEvent,
  };
}
