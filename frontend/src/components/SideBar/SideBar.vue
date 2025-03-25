<template>
  <v-navigation-drawer
    :model-value="drawer"
    @update:model-value="(value) => $emit('update:drawer', value)"
  >
    <v-list>
      <v-list-item
        v-for="season in seasons"
        :key="season.value"
        :title="season.title"
        @click="navigateToSeason(season.value)"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useSideBar } from '@/components/SideBar/useSideBar.ts';

defineProps<{ drawer: boolean }>();
defineEmits(['update:drawer']);
const { seasons, navigateToSeason } = useSideBar();
</script>
