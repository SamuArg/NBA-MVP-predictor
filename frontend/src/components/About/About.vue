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
              The NBA MVP Predictor uses machine learning to forecast the
              NBA's Most Valuable Player award winner. It combines historical
              voting results with player and team statistics to rank the top
              ten candidates. The home page shows the current race (or the
              latest season with data when the new season has not started
              yet), and the side menu opens any season back to 1981.
            </p>

            <div class="text-h6 mb-2">
              How it works
            </div>
            <p class="mb-4">
              Our prediction engine is a Multi Layer Perceptron built with
              PyTorch. For every season it estimates an MVP share for each
              player and converts the leading shares into probability
              percentages. The model is trained season by season, always
              excluding the season being predicted, to avoid leaking the
              result into the training data. Predictions are refreshed daily
              while the season is in progress.
            </p>

            <div class="text-h6 mb-2 mt-4">
              Statistical analysis
            </div>
            <p class="mb-4">
              Analysis of MVP voting patterns highlights the metrics that
              matter most: VORP (Value Over Replacement Player), PER (Player
              Efficiency Rating), team seed, BPM (Box Plus/Minus) and team win
              percentage. That matches historical voting trends, where voters
              weigh both individual excellence and team success. The plot below
              shows the features a random forest regressor relies on most; its
              agreement rate is approximately 65%.
            </p>
            <v-img
              src="@/assets/importance.png"
              alt="Feature importance chart"
              class="rounded mb-4"
            />

            <div class="text-h6 mb-2 mt-4">
              Reading the results
            </div>
            <ul class="mb-4 pl-6">
              <li class="mb-2">
                Click a date on the progression chart to see that day's
                rankings.
              </li>
              <li class="mb-2">
                Historical pages also show the official MVP voting shares for
                comparison with the model's predictions.
              </li>
              <li>
                Probabilities are estimates, not guarantees. Early-season
                predictions are naturally less stable than late-season ones.
              </li>
            </ul>

            <div class="text-h6 mb-2 mt-4">
              Data sources
            </div>
            <p class="mb-4">
              Predictions are powered by NBA statistics from
              <a href="https://www.basketball-reference.com/">Basketball Reference</a>.
              Custom scraping tools gather advanced statistics, team
              standings, per-game numbers and historical MVP voting data.
            </p>
          </v-card-text>

          <v-card-actions>
            <v-btn
              color="primary"
              href="https://github.com/SamuArg/NBA-MVP-predictor"
              target="_blank"
              rel="noopener noreferrer"
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
