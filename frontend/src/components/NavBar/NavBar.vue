<template>
  <v-app-bar
    flat
    density="comfortable"
  >
    <v-app-bar-nav-icon
      aria-label="Open seasons menu"
      @click.stop="drawer = !drawer"
    />
    <v-app-bar-title class="font-weight-bold">
      NBA MVP Predictor
    </v-app-bar-title>

    <template #append>
      <v-btn
        to="/"
        variant="text"
        prepend-icon="mdi-basketball"
        class="d-none d-sm-flex"
      >
        Predictions
      </v-btn>
      <v-btn
        to="/about"
        variant="text"
        prepend-icon="mdi-information-outline"
        class="d-none d-sm-flex"
      >
        About
      </v-btn>
      <v-btn
        icon="mdi-github"
        aria-label="Open the GitHub repository"
        @click="handleGithubClick"
      />
    </template>
  </v-app-bar>

  <SideBar v-model:drawer="drawer" />
</template>

<script lang="ts" setup>
import { useNavBar } from './useNavBar';

const { handleGithubClick, drawer } = useNavBar();
</script>
