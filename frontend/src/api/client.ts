const DEFAULT_API_URL = 'https://nba-mvp-predictions-0354ab92b6ca.herokuapp.com/';

const DEFAULT_DEV_API_URL = '/api/';

const DEFAULT_TIMEOUT_MS = 45_000;

function normalizeBaseUrl(url: string | undefined): string {
  const value = (url ?? '').trim();
  const base =
    value || (import.meta.env.DEV ? DEFAULT_DEV_API_URL : DEFAULT_API_URL);
  return base.endsWith('/') ? base : `${base}/`;
}

/**
 * The deployed backend is used by default so the production build keeps
 * working even when no environment variables are configured. During local
 * development the Vite proxy is used to avoid CORS restrictions, unless a
 * full API URL is provided explicitly.
 */
export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_URL);

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface RequestOptions {
  timeoutMs?: number;
  retries?: number;
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function readErrorPayload(response: Response): Promise<unknown> {
  try {
    const text = await response.text();
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

async function requestOnce<T>(url: string, timeoutMs: number): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });

    if (!response.ok) {
      const payload = await readErrorPayload(response);
      const message =
        payload &&
        typeof payload === 'object' &&
        'error' in payload &&
        typeof payload.error === 'string'
          ? payload.error
          : `The prediction API returned an error (${response.status}).`;
      throw new ApiError(message, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('The prediction API took too long to respond.');
    }

    throw new ApiError('Unable to reach the prediction API.');
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Fetch JSON from the prediction API with a timeout and one retry for
 * transient failures (cold starts, 5xx responses, network hiccups).
 */
export async function fetchJson<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const url = `${API_BASE_URL}${path.replace(/^\/+/, '')}`;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const retries = options.retries ?? 1;

  let lastError = new ApiError('Unable to reach the prediction API.');

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      return await requestOnce<T>(url, timeoutMs);
    } catch (error) {
      lastError =
        error instanceof ApiError
          ? error
          : new ApiError('Unable to reach the prediction API.');

      const isRetryable = lastError.status === 0 || lastError.status >= 500;
      if (!isRetryable || attempt === retries) throw lastError;

      await delay(600 * (attempt + 1));
    }
  }

  throw lastError;
}
