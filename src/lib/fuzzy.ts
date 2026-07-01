export function normalizeEn(s: string): string {
  return s
    .toLowerCase()
    .trim()
    .replace(/[.,!?;:"']/g, "")
    .replace(/\s+/g, " ");
}

// Damerau-Levenshtein-ish (basic Levenshtein).
export function levenshtein(a: string, b: string): number {
  if (a === b) return 0;
  const m = a.length;
  const n = b.length;
  if (!m) return n;
  if (!n) return m;
  const dp = new Array(n + 1);
  for (let j = 0; j <= n; j++) dp[j] = j;
  for (let i = 1; i <= m; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= n; j++) {
      const tmp = dp[j];
      dp[j] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[j], dp[j - 1]);
      prev = tmp;
    }
  }
  return dp[n];
}

export function matchEn(input: string, expected: string): "exact" | "close" | "wrong" {
  const a = normalizeEn(input);
  const b = normalizeEn(expected);
  if (!a) return "wrong";
  if (a === b) return "exact";
  const dist = levenshtein(a, b);
  const tol = b.length <= 4 ? 1 : b.length <= 8 ? 2 : 3;
  return dist <= tol ? "close" : "wrong";
}
