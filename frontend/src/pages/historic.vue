<template>
  <Base :key="season">
    <h1
      v-if="Number(season)"
      class="text-h4 mt-4 text-center"
    >
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
import { useRoute, useRouter } from 'vue-router';
import { watch } from 'vue';
import { getSeason } from '@/api/mvps.ts';

const route = useRoute();
const router = useRouter();
const season = ref(route.query.season as string);

async function validateSeason(newSeason: string | null) {
  try {
    const currentSeason = await getSeason();
    if (!newSeason) {
      throw new Error('No season specified');
    }
    if (!Number(newSeason)) {
      throw new Error('Season is not a number');
    }
    if (Number(newSeason) < 1981 || Number(newSeason) > Number(currentSeason)) {
      throw new Error('Season specified is not available.');
    }
    season.value = newSeason;
  } catch (error) {
    console.error(error);
    await router.push('/');
  }
}

watch(() => route.query.season as string, validateSeason);
onMounted(() => validateSeason(route.query.season as string));

</script>
