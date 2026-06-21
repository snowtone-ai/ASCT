#!/usr/bin/env node
/**
 * .claude/hooks/guard.mjs -- PreToolUse deny-set guard
 * pm-zero v10
 *
 * Deterministically blocks the dangerous set regardless of conversation state.
 * A prompt instruction can be summarized away by compaction; a hook cannot.
 * Reads the Claude Code PreToolUse JSON payload from stdin, inspects the command,
 * and exits 2 to block (stderr is surfaced to the model) or 0 to allow.
 */
import { warnHookFailure } from '../../scripts/lib/redact.mjs';

// Dangerous patterns covering both Bash and PowerShell invocations.
const DENY = [
  { re: /git\s+push\s+(--force\b|--force-with-lease|-\w*f)/i, msg: 'Force-push is blocked. Use a standard push.' },
  { re: /git\s+reset\s+--hard/i, msg: 'git reset --hard is blocked (history is the audit trail).' },
  { re: /git\s+clean\s+-\w*f/i, msg: 'git clean -f is blocked.' },
  { re: /\brm\s+-\w*r\w*f?\w*\s+[\/~]/i, msg: 'Recursive delete of root/home is blocked.' },
  { re: /Remove-Item\b(?=.*-Recurse\b)(?=.*-Force\b).*(\s[\/~]|[A-Za-z]:\\)/i, msg: 'Recursive force delete of a root/drive path is blocked.' },
  { re: /\b(drop|truncate)\s+(table|database|schema)\b/i, msg: 'Destructive DB op requires an explicit logged decision.' },
  { re: /(cat|type|Get-Content|Read-Host)\b.*\.env(\.|\b)/i, msg: 'Reading .env / secrets is blocked.' },
];

async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (c) => (data += c));
    process.stdin.on('end', () => resolve(data));
    setTimeout(() => resolve(data), 100);
  });
}

function extractCommand(payload) {
  try {
    const obj = JSON.parse(payload);
    const input = obj.tool_input ?? obj.toolInput ?? obj.input ?? {};
    return input.command ?? input.cmd ?? input.script ?? '';
  } catch {
    return payload; // fall back to raw text scan
  }
}

try {
  const raw = await readStdin();
  const command = extractCommand(raw);
  for (const { re, msg } of DENY) {
    if (re.test(command)) {
      process.stderr.write(`[guard] Blocked: ${msg}\n`);
      process.exit(2);
    }
  }
  process.exit(0);
} catch (err) {
  warnHookFailure('PreToolUse/guard', err);
  process.exit(0); // fail open: do not block on guard error
}
