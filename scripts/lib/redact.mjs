/**
 * scripts/lib/redact.mjs -- Single source for secret redaction
 * Used by both Claude and Codex dispatchers.
 */

const REDACT_PATTERNS = [
  /sk-[a-zA-Z0-9_-]{20,}/g,
  /gh[psuor]_[a-zA-Z0-9_]{20,}/g,
  /Bearer\s+[a-zA-Z0-9._-]+/gi,
  /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,
  /(password|token|secret|key|authorization)["':=\s]+["']?[^"'\s,}]{8,}/gi,
];

export function redact(text) {
  if (typeof text !== 'string') return text;
  let result = text;
  for (const pattern of REDACT_PATTERNS) {
    result = result.replace(pattern, '[REDACTED]');
  }
  return result;
}

export function warnHookFailure(scope, error) {
  const msg = error instanceof Error ? error.message : String(error);
  console.warn(`[hook-warning] ${scope}: ${redact(msg)}`);
}
