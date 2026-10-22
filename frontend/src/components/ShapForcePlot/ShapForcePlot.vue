<template>
  <div class="force">
    <div class="force__summary">
      <span>
        Average qualifying player
        <strong>{{ formatScore(explanation.baseValue) }}</strong>
      </span>
      <span class="force__arrow">→</span>
      <span>
        {{ explanation.player }}
        <strong>{{ formatScore(explanation.outputValue) }}</strong>
      </span>
    </div>

    <div
      class="force__track"
      role="img"
      :aria-label="`SHAP force plot from ${formatScore(explanation.baseValue)} to ${formatScore(explanation.outputValue)}`"
    >
      <div
        v-for="segment in segments"
        :key="segment.key"
        class="force__segment"
        :class="segment.positive ? 'force__segment--up' : 'force__segment--down'"
        :style="{ left: `${segment.leftPct}%`, width: `${segment.widthPct}%` }"
        :title="segment.title"
      >
        <span v-if="segment.widthPct >= 7">{{ segment.label }}</span>
      </div>

      <div
        class="force__marker force__marker--base"
        :style="{ left: `${basePct}%` }"
        title="Base value (average qualifying player)"
      />
      <div
        class="force__marker force__marker--output"
        :style="{ left: `${outputPct}%` }"
        title="Model score"
      />
    </div>

    <div class="force__footer">
      <span class="force__legend">
        <span class="force__swatch force__swatch--up" />
        Pushes score up
      </span>
      <span class="force__legend">
        <span class="force__swatch force__swatch--down" />
        Pushes score down
      </span>
      <span class="force__net">
        Net {{ formatImpact(explanation.outputValue - explanation.baseValue) }}
      </span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type {
  FeatureContribution,
  PlayerExplanation,
} from '@/api/mvps';

const props = defineProps<{
  explanation: PlayerExplanation;
}>();

const MAX_SEGMENTS = 10;

interface ForceFeature extends FeatureContribution {
  key: string;
}

interface ForceSegment {
  key: string;
  label: string;
  positive: boolean;
  leftPct: number;
  widthPct: number;
  title: string;
}

function formatScore(value: number) {
  return Number.isFinite(value) ? value.toFixed(3) : '—';
}

function formatImpact(value: number) {
  if (!Number.isFinite(value)) return '—';
  const sign = value >= 0 ? '+' : '−';
  return `${sign}${Math.abs(value).toFixed(3)}`;
}

const selectedFeatures = computed<ForceFeature[]>(() => {
  const ranked = props.explanation.features
    .filter((feature) => Math.abs(feature.contribution) > 1e-9)
    .sort(
      (left, right) =>
        Math.abs(right.contribution) - Math.abs(left.contribution),
    );

  const selected: ForceFeature[] = ranked
    .slice(0, MAX_SEGMENTS)
    .map((feature) => ({ ...feature, key: feature.name }));

  const remainder = ranked.slice(MAX_SEGMENTS);
  if (remainder.length > 0) {
    const contribution = remainder.reduce(
      (total, feature) => total + feature.contribution,
      0,
    );
    if (Math.abs(contribution) > 1e-9) {
      selected.push({
        key: '__other__',
        name: '__other__',
        label: 'Other features',
        value: null,
        displayValue: '',
        contribution,
      });
    }
  }

  return selected;
});

const positives = computed(() =>
  selectedFeatures.value
    .filter((feature) => feature.contribution > 0)
    .sort((left, right) => right.contribution - left.contribution),
);

const negatives = computed(() =>
  selectedFeatures.value
    .filter((feature) => feature.contribution < 0)
    .sort((left, right) => left.contribution - right.contribution),
);

const positiveTotal = computed(() =>
  positives.value.reduce((total, feature) => total + feature.contribution, 0),
);

const negativeTotal = computed(() =>
  negatives.value.reduce((total, feature) => total + feature.contribution, 0),
);

const scale = computed(() => {
  const minimum = Math.min(0, negativeTotal.value);
  const maximum = Math.max(0, positiveTotal.value);
  const span = maximum - minimum;
  const padding = span > 0 ? span * 0.06 : 1;

  return {
    minimum: minimum - padding,
    span: span + padding * 2,
  };
});

function toPercent(value: number) {
  return ((value - scale.value.minimum) / scale.value.span) * 100;
}

const segments = computed<ForceSegment[]>(() => {
  const result: ForceSegment[] = [];

  let cursor = 0;
  for (const feature of negatives.value) {
    const next = cursor + feature.contribution;
    result.push({
      key: feature.key,
      label: feature.label,
      positive: false,
      leftPct: toPercent(next),
      widthPct: toPercent(cursor) - toPercent(next),
      title: `${feature.label}: ${formatImpact(feature.contribution)}${
        feature.displayValue ? ` (${feature.displayValue})` : ''
      }`,
    });
    cursor = next;
  }

  cursor = 0;
  for (const feature of positives.value) {
    const next = cursor + feature.contribution;
    result.push({
      key: feature.key,
      label: feature.label,
      positive: true,
      leftPct: toPercent(cursor),
      widthPct: toPercent(next) - toPercent(cursor),
      title: `${feature.label}: ${formatImpact(feature.contribution)}${
        feature.displayValue ? ` (${feature.displayValue})` : ''
      }`,
    });
    cursor = next;
  }

  return result;
});

const basePct = computed(() => toPercent(0));
const outputPct = computed(() =>
  toPercent(positiveTotal.value + negativeTotal.value),
);
</script>

<style scoped>
.force {
  width: 100%;
}

.force__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
  color: #cfcfcf;
  font-size: 13px;
  margin-bottom: 10px;
}

.force__summary strong {
  color: #ffffff;
  font-variant-numeric: tabular-nums;
}

.force__arrow {
  color: #f5a623;
  font-size: 16px;
}

.force__track {
  position: relative;
  height: 48px;
  border-radius: 6px;
  background:
    linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.045) 0%,
      rgba(255, 255, 255, 0.02) 50%,
      rgba(255, 255, 255, 0.045) 100%
    );
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.force__segment {
  position: absolute;
  top: 8px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-sizing: border-box;
  border-radius: 3px;
  color: #ffffff;
  font-size: 11px;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition:
    width 0.3s ease,
    left 0.3s ease;
}

.force__segment--up {
  background: linear-gradient(180deg, #ef5350 0%, #c62828 100%);
}

.force__segment--down {
  background: linear-gradient(180deg, #64b5f6 0%, #1565c0 100%);
}

.force__marker {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  pointer-events: none;
}

.force__marker--base {
  border-left: 1px dashed rgba(255, 255, 255, 0.75);
}

.force__marker--output {
  border-left: 2px solid #f5a623;
}

.force__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 8px;
  color: #9e9e9e;
  font-size: 12px;
}

.force__legend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.force__swatch {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  display: inline-block;
}

.force__swatch--up {
  background: #ef5350;
}

.force__swatch--down {
  background: #64b5f6;
}

.force__net {
  margin-left: auto;
  color: #e0e0e0;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 600px) {
  /* The bar gets too narrow for readable labels on phones; the driver table
     below carries the details instead. */
  .force__segment span {
    display: none;
  }
}
</style>
