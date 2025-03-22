<template>
  <v-app-bar>
    <v-app-bar-nav-icon></v-app-bar-nav-icon>
    <v-title>NBA MVP Predictor</v-title>
    <template v-slot:append>
      <v-btn @click="handleGithubClick" icon="mdi-github"></v-btn>
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { useNavBar } from "./useNavBar";
const { handleGithubClick } = useNavBar();
</script>
