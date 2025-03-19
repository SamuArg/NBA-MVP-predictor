import { ref, onMounted } from "vue";
import type { MVPResponse } from "@/api/mvps";
import { getPredictionsSeason } from "@/api/mvps";
import { useAppStore } from "@/stores/app";

export function useMvpChart() {
  const chartOptions = ref({});
  const store = useAppStore();
  const loading = computed(() => store.loading);

  const transformData = (data: MVPResponse[]) => {
    const dates = data.map((entry) => entry.date);
    const lastDayData = data[data.length - 1];
    if (!lastDayData) return { dates, series: [], players: [] };

    const topPlayers = lastDayData.predictions
      .sort((a, b) => b.probability - a.probability)
      .slice(0, 10)
      .map((p) => p.player);

    const series = topPlayers.map((player) => ({
      name: player,
      type: "line",
      data: data.map((entry) => {
        const found = entry.predictions.find((p) => p.player === player);
        return found ? found.probability : 0;
      }),
    }));

    return { dates, series, players: topPlayers };
  };

  onMounted(async () => {
    try {
      const rawData = await getPredictionsSeason("2025");
      if (rawData) {
        const { dates, series, players } = transformData(rawData);
        chartOptions.value = {
          tooltip: {
            trigger: "axis",
            formatter: (params: any[]) =>
              params
                .sort((a, b) => b.value - a.value)
                .map(
                  (item) =>
                    `${item.marker} ${item.seriesName}: ${item.value.toFixed(2)}`,
                )
                .join("<br>"),
          },
          legend: { data: players, textStyle: { color: "white" } },
          xAxis: {
            type: "category",
            data: dates,
            axisPointer: { show: true, snap: true },
            triggerEvent: true,
          },
          yAxis: { type: "value", min: 0 },
          series,
        };
      }
      store.setLoading(false);
    } catch (error) {
      console.error("Error fetching MVP probabilities:", error);
      store.setLoading(false);
    }
  });

  const onChartClick = (params: any) => {
    if (params.componentType === "xAxis") {
      store.setSelectedDate(params.value);
    }
  };

  return { loading, chartOptions, onChartClick };
}
