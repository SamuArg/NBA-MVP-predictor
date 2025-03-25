<template>
  <Base :key="season">
    <h1 class="text-h4 mt-4 text-center">
      Season {{ season }}
    </h1>
    <ChartPrediction
      :season="season"
      :show-ranking="true"
    />
  </Base>
</template>

<script setup lang="ts">
import Base from '@/layouts/Base.vue';
import { useRoute } from 'vue-router';
import { watch } from 'vue';

const route = useRoute();
const season = ref(route.query.season as string);
watch(() => route.query.season, (newSeason) => {
  if (newSeason) {
    season.value = newSeason as string;
  }
});
</script>
