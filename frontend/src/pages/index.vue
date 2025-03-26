<template>
  <Base>
    <ChartPrediction
      v-if="season"
      :season="season"
      :show-ranking="false"
    />
  </Base>
</template>

<script lang="ts" setup>
import Base from '@/layouts/Base.vue';
import { getSeason } from '@/api/mvps.ts';
import { ref, onMounted } from 'vue';

const season = ref<string>('');
onMounted(async () => {
  const response = await getSeason();
  season.value = String(response);
});
</script>
