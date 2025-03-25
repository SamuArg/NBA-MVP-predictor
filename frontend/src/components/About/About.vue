<template>
  <v-container>
    <v-row justify="center">
      <v-col
        cols="12"
        md="8"
      >
        <v-card class="pa-4">
          <v-card-title class="text-h4 mb-4">
            MVP Predictor
          </v-card-title>

          <v-card-text>
            <div class="text-h6 mb-2">
              Overview
            </div>
            <p class="mb-4">
              The NBA MVP Predictor leverages advanced machine learning
              techniques to forecast the NBA's Most Valuable Player award
              winner. Using comprehensive historical data and real-time
              statistics, our model analyzes player performance throughout the
              season. View current MVP race predictions on our main page, or
              explore historical predictions dating back to 1981 through our
              interactive side menu.
            </p>

            <div class="text-h6 mb-2">
              Model Details
            </div>
            <p class="mb-4">
              Our prediction engine employs a Multi Layer Perceptron model from sk-learn that
              calculates MVP share probabilities for each player. The model
              analyzes daily performance metrics to rank the top 10 MVP
              candidates, converting raw MVP share calculations into probability
              percentages. With a 72% accuracy rate in predicting past MVP
              winners, our model has proven to be highly reliable in identifying
              MVP-caliber performance.
            </p>

            <div class="text-h6 mb-2 mt-4">
              Statistical Analysis
            </div>
            <p class="mb-4">
              Through extensive analysis of MVP voting patterns, we've
              identified the key factors that influence MVP selection. The
              visualization below reveals the five most influential metrics:
              VORP (Value Over Replacement Player), PER (Player Efficiency
              Rating), Team Seed, BPM (Box Plus/Minus), and Team Win Percentage.
              This aligns with historical voting trends, where voters heavily
              weigh both individual excellence and team success. The plot shows
              the most important features that a random forest regressor uses to make
              his prediction. His accuracy is about 65%.
            </p>
            <img
              src="@/assets/importance.png"
              alt="Feature Importance Chart"
            >

            <div class="text-h6 mb-2 mt-4">
              Data Sources
            </div>
            <p class="mb-4">
              Our predictions are powered by comprehensive NBA statistics from
              <a href="https://www.basketball-reference.com/">Basketball Reference</a>. We utilize custom web scraping
              tools to gather and process
              advanced statistics, team standings, and historical MVP voting
              data, ensuring our predictions are based on the most accurate and
              up-to-date information available.
            </p>
          </v-card-text>
          <v-card-actions>
            <v-btn
              color="primary"
              href="https://github.com/SamuArg/NBA-MVP-predictor"
              target="_blank"
              prepend-icon="mdi-github"
            >
              View on GitHub
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts"></script>
