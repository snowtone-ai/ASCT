#!/usr/bin/env node
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'

const isWindows = process.platform === 'win32'
const shell = isWindows ? 'powershell.exe' : true

const requiredPaths = [
  'AGENTS.md',
  'CLAUDE.md',
  'HANDOFF-JA.md',
  'tasks.md',
  'docs/vision.md',
  'docs/state.md',
  'docs/decisions.md',
  'docs/issues.md',
  'docs/repo-map.md',
  '.claude/settings.json',
]

const commands = [
  ['ruff', ['check', 'src/', 'tests/'], 'Lint'],
  ['pyright', ['src/'], 'Typecheck'],
  ['pytest', ['--tb=short', '-q'], 'Tests'],
]

function run(command, args, label) {
  return new Promise((resolve) => {
    console.log(`\n--- ${label} ---`)
    const child = spawn(command, args, { stdio: 'inherit', shell })
    child.on('close', (code) => resolve({ label, ok: code === 0, code }))
    child.on('error', (error) => {
      console.error(`${label}: ${error.message}`)
      resolve({ label, ok: false, code: -1 })
    })
  })
}

const results = []

console.log('=== ASCT verification ===')
for (const file of requiredPaths) {
  const ok = existsSync(file)
  console.log(`${ok ? 'OK' : 'MISSING'} ${file}`)
  if (!ok) results.push({ label: `required:${file}`, ok: false, code: 1 })
}

for (const [command, args, label] of commands) {
  results.push(await run(command, args, label))
}

const failed = results.filter((result) => !result.ok)
if (failed.length > 0) {
  for (const result of failed) {
    console.error(`[verify] ${result.label} failed with exit ${result.code}`)
  }
  process.exit(1)
}

console.log('[verify] all checks passed')
