import { ApiError, fetchJson } from '@/api/client';

export interface Prediction {
  player: string;
  probability: number;
  team: string;
}

export interface SeasonPrediction {
  date: string;
  predictions: Prediction[];
  season: number;
}

export interface RankingEntry {
  player: string;
  probability: number;
  team: string;
}

export interface SeasonInfo {
  season: number;
  predictions: number;
  firstDate: string;
  lastDate: string;
  hasRanking: boolean;
}

export interface SeasonCatalogue {
  current: number | null;
  latest: number | null;
  seasons: SeasonInfo[];
}

function asArray(payload: unknown): unknown[] {
  return Array.isArray(payload) ? payload : [];
}

function toNumber(value: unknown, fallback = 0): number {
  const numberValue = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

function toPositiveInteger(value: unknown): number | null {
  const numberValue = toNumber(value, Number.NaN);
  return Number.isInteger(numberValue) && numberValue > 0 ? numberValue : null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function normalizePredictions(payload: unknown): Prediction[] {
  return asArray(payload)
    .filter(isRecord)
    .map((entry) => ({
      player: String(entry.player ?? ''),
      probability: toNumber(entry.probability),
      team: String(entry.team ?? ''),
    }))
    .filter((entry) => entry.player.length > 0);
}

function normalizeSeasonEntries(
  payload: unknown,
  fallbackSeason: number,
): SeasonPrediction[] {
  return asArray(payload)
    .filter(isRecord)
    .map((entry) => ({
      date: String(entry.date ?? ''),
      season: toNumber(entry.season, fallbackSeason),
      predictions: normalizePredictions(entry.predictions),
    }))
    .filter((entry) => entry.date.length > 0)
    .sort((a, b) => a.date.localeCompare(b.date));
}

function normalizeSeasonCatalogue(payload: unknown): SeasonCatalogue | null {
  if (!isRecord(payload) || !Array.isArray(payload.seasons)) return null;

  const seasons: SeasonInfo[] = payload.seasons
    .filter(isRecord)
    .map((entry) => {
      const season = toPositiveInteger(entry.season);
      return {
        season: season ?? 0,
        predictions: toNumber(entry.predictions),
        firstDate: String(entry.firstDate ?? ''),
        lastDate: String(entry.lastDate ?? ''),
        hasRanking: Boolean(entry.hasRanking),
      };
    })
    .filter((entry) => entry.season > 0)
    .sort((a, b) => b.season - a.season);

  const latest = toPositiveInteger(payload.latest) ?? seasons[0]?.season ?? null;

  return {
    current: toPositiveInteger(payload.current),
    latest,
    seasons,
  };
}

/**
 * Get predictions for a single date.
 *
 * Returns an empty array when the date has no data.
 */
export const getPredictionsDate = async (
  date: string,
): Promise<Prediction[]> => {
  try {
    const payload = await fetchJson<unknown>(
      `mvps?date=${encodeURIComponent(date)}`,
    );
    return normalizePredictions(payload);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return [];
    throw error;
  }
};

/**
 * Get every prediction for a season, sorted from oldest to newest.
 *
 * The currently deployed API answers 200 with a message string for seasons
 * without data, while the new API answers 404. Both are normalized to [].
 */
export const getSeasonPredictions = async (
  season: number,
): Promise<SeasonPrediction[]> => {
  try {
    const payload = await fetchJson<unknown>(`mvps?season=${season}`);
    return normalizeSeasonEntries(payload, season);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return [];
    throw error;
  }
};

export const getLatestPredictions = async (): Promise<Prediction[]> => {
  try {
    const payload = await fetchJson<unknown>('mvps');
    return normalizePredictions(payload);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return [];
    throw error;
  }
};

export const getAllPredictions = async (): Promise<SeasonPrediction[]> => {
  const payload = await fetchJson<unknown>('');
  return normalizeSeasonEntries(payload, 0);
};

export const getMvpRanking = async (
  season: number,
): Promise<RankingEntry[]> => {
  try {
    const payload = await fetchJson<unknown>(`ranking?season=${season}`);
    return asArray(payload)
      .filter(isRecord)
      .map((entry) => ({
        player: String(entry.player ?? ''),
        // Official voting shares are stored as strings, e.g. "0.913".
        probability: toNumber(entry.probability),
        team: String(entry.team ?? ''),
      }))
      .filter((entry) => entry.player.length > 0);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return [];
    throw error;
  }
};

export const getCurrentSeason = async (): Promise<number | null> => {
  try {
    const payload = await fetchJson<unknown>('season');
    return toPositiveInteger(payload);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 400)) {
      return null;
    }
    throw error;
  }
};

async function buildCatalogueFromHistory(): Promise<SeasonCatalogue> {
  const entries = await getAllPredictions();
  const bySeason = new Map<number, SeasonInfo>();

  for (const entry of entries) {
    if (!entry.season) continue;

    const existing = bySeason.get(entry.season);
    if (existing) {
      existing.predictions += 1;
      if (entry.date < existing.firstDate) existing.firstDate = entry.date;
      if (entry.date > existing.lastDate) existing.lastDate = entry.date;
    } else {
      bySeason.set(entry.season, {
        season: entry.season,
        predictions: 1,
        firstDate: entry.date,
        lastDate: entry.date,
        hasRanking: false,
      });
    }
  }

  const seasons = [...bySeason.values()].sort(
    (a, b) => b.season - a.season,
  );

  let current: number | null = null;
  try {
    current = await getCurrentSeason();
  } catch {
    // The season catalogue can still be used without the current season.
  }

  return {
    current,
    latest: seasons[0]?.season ?? null,
    seasons,
  };
}

/**
 * Get the list of seasons that have predictions.
 *
 * Uses the lightweight /seasons endpoint when the backend supports it and
 * falls back to the legacy "all predictions" endpoint otherwise, which keeps
 * the frontend compatible with older backend deployments.
 */
export const getSeasons = async (): Promise<SeasonCatalogue> => {
  try {
    const payload = await fetchJson<unknown>('seasons');
    const catalogue = normalizeSeasonCatalogue(payload);
    if (catalogue) return catalogue;
  } catch (error) {
    if (
      !(error instanceof ApiError) ||
      (error.status !== 404 && error.status !== 400)
    ) {
      throw error;
    }
  }

  return buildCatalogueFromHistory();
};
