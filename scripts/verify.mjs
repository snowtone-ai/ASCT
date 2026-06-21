#!/usr/bin/env node
/**
 * scripts/verify.mjs -- pm-zero v10 unified verification entry point
 * Adapted for Python/FastAPI (ASCT project)
 */
import { spawn } from 'node:child_process';
import { readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';

const isWindows = process.platform === 'win32';

function run(cmd, args, label) {
  return new Promise((resolve) => {
    console.log(`\n--- ${label} ---`);
    const proc = spawn(cmd, args, {
      stdio: 'inherit',
      shell: isWindows ? 'powershell.exe' : true,
    });
    proc.on('close', (code) => {
      const status = code === 0 ? 'PASS' : 'FAIL';
      console.log(`${label}: ${status} (exit ${code})`);
      resolve({ label, code, pass: code === 0 });
    });
    proc.on('error', (err) => {
      console.log(`${label}: ERROR - ${err.message}`);
      resolve({ label, code: -1, pass: false });
    });
  });
}

async function main() {
  const results = [];

  // 1. Check directory structure
  console.log('=== ASCT Verification ===\n');
  const requiredDirs = ['src', 'src/models', 'src/agents', 'src/orchestrator', 'tests', 'configs', 'docs'];
  for (const dir of requiredDirs) {
    const exists = existsSync(dir);
    console.log(`  ${exists ? 'OK' : 'MISSING'}: ${dir}`);
    if (!exists) results.push({ label: `dir:${dir}`, code: 1, pass: false });
  }

  // 2. v10 core/ledger integrity check
  const coreFiles = [
    'CLAUDE.md',
    '.claude/settings.json',
    '.claude/hooks/guard.mjs',
    'tasks.md',
    'docs/state.md',
    'docs/repo-map.md',
    'HANDOFF-JA.md',
  ];
  for (const f of coreFiles) {
    const exists = existsSync(f);
    console.log(`  ${exists ? 'OK' : 'MISSING'}: ${f}`);
    if (!exists) results.push({ label: `file:${f}`, code: 1, pass: false });
  }

  // 3. Lint
  results.push(await run('ruff', ['check', 'src/', 'tests/'], 'Lint (ruff)'));

  // 4. Type check (optional, only if pyright installed)
  results.push(await run('pyright', ['src/'], 'Typecheck (pyright)'));

  // 5. Tests
  results.push(await run('pytest', ['--tb=short', '-q'], 'Tests (pytest)'));

  // 6. Summary
  console.log('\n=== Summary ===');
  const failures = results.filter((r) => !r.pass);
  if (failures.length === 0) {
    console.log('All checks passed.');
    process.exit(0);
  } else {
    console.log(`${failures.length} check(s) failed:`);
    for (const f of failures) {
      console.log(`  FAIL: ${f.label}`);
    }
    process.exit(1);
  }
}

main();
