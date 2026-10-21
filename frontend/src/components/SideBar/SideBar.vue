<template>
  <v-navigation-drawer
    :model-value="drawer"
    width="290"
    @update:model-value="emit('update:drawer', $event)"
  >
    <v-list
      nav
      density="compact"
    >
      <v-list-subheader>MVP races</v-list-subheader>

      <v-list-item
        to="/"
        prepend-icon="mdi-basketball"
        title="Current race"
        @click="closeDrawer"
      />

      <v-list-item
        to="/about"
        prepend-icon="mdi-information-outline"
        title="About"
        @click="closeDrawer"
      />

      <v-divider class="my-2" />

      <v-list-subheader>Seasons</v-list-subheader>

      <v-list-item
        v-if="loading && seasons.length === 0"
        title="Loading seasons…"
        disabled
      />

      <v-list-item
        v-else-if="error && seasons.length === 0"
        :title="error"
        disabled
      />

      <v-list-item
        v-for="item in seasons"
        :key="item.season"
        :to="{ path: '/historic', query: { season: String(item.season) } }"
        :title="formatSeasonLabel(item.season)"
        :subtitle="formatTrackedDays(item.predictions)"
        :active="item.season === activeSeason"
        @click="closeDrawer"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useSideBar } from '@/components/SideBar/useSideBar.ts';
import { formatSeasonLabel, formatTrackedDays } from '@/utils/format';

defineProps<{ drawer: boolean }>();
const emit = defineEmits<{ 'update:drawer': [value: boolean] }>();

const { seasons, loading, error, activeSeason } = useSideBar();

function closeDrawer() {
  emit('update:drawer', false);
}
</script>
