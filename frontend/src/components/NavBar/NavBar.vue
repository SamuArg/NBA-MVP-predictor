<template>
  <v-app-bar>
    <v-app-bar-nav-icon />
    <v-app-bar-title>NBA MVP Predictor</v-app-bar-title>
    <template #append>
      <v-btn to="/">
        Predictions
      </v-btn>
      <v-btn to="/about">
        About
      </v-btn>
      <v-btn
        icon="mdi-github"
        @click="handleGithubClick"
      />
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { useNavBar } from "./useNavBar";
const { handleGithubClick } = useNavBar();
</script>
