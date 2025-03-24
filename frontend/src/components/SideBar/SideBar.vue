<template>
  <v-navigation-drawer
    :model-value="drawer"
    @update:model-value="(value) => $emit('update:drawer', value)"
  >
    <v-list :items="seasons" />
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useSideBar } from '@/components/SideBar/useSideBar.ts';

defineProps<{ drawer: boolean }>();
defineEmits(['update:drawer']);
const { seasons } = useSideBar();
</script>
