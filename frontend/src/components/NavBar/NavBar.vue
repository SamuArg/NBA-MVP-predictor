<template>
  <v-app-bar>
    <v-app-bar-nav-icon></v-app-bar-nav-icon>
    <v-app-bar-title>NBA MVP Predictor</v-app-bar-title>
    <template v-slot:append>
      <v-btn to="/">Predictions</v-btn>
      <v-btn @click="handleGithubClick" icon="mdi-github"></v-btn>
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { useNavBar } from "./useNavBar";
const { handleGithubClick } = useNavBar();
</script>
