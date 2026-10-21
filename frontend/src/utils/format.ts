export function formatSeasonLabel(season: number | string | null | undefined) {
  const value = Number(season);
  if (!Number.isFinite(value) || value <= 0) return '—';
  return `${value - 1}-${String(value).slice(-2)}`;
}

export function formatTrackedDays(days: number) {
  if (!Number.isFinite(days) || days <= 0) return 'No days tracked';
  return `${days} ${days === 1 ? 'day' : 'days'} tracked`;
}

export function formatPercentage(value: number, digits = 1) {
  if (!Number.isFinite(value)) return '—';
  return `${value.toFixed(digits)}%`;
}

export function formatShare(value: number) {
  if (!Number.isFinite(value)) return '—';
  return value.toFixed(3);
}

export function formatDate(date: string) {
  if (!date) return '—';

  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;

  return parsed.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
