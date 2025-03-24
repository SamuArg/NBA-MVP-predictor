<template>
  <v-navigation-drawer
    :model-value="drawer"
    @update:model-value="(value) => $emit('update:drawer', value)"
  >
    <v-list :items="seasons" />
  </v-navigation-drawer>
</template>

<script setup lang="ts">
defineProps<{ drawer: boolean }>();
defineEmits(['update:drawer']);

const seasons = [
  {
    title: '2025',
    value: '2025',
  },
  {
    title: '2024',
    value: '2024',
  },
  {
    title: '2023',
    value: '2023',
  },
  {
    title: '2022',
    value: '2022',
  },
];
</script>
