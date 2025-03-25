<template>
  <Base>
    <ChartPrediction :season="season" />
  </Base>
</template>

<script setup lang="ts">
import Base from '@/layouts/Base.vue';
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();
const season = computed(() => route.query.season as string | undefined);
</script>
