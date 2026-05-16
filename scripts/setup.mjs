#!/usr/bin/env node
import fs from 'node:fs/promises'

const dirs = [
  'docs',
  'scripts',
  'screenshots',
  'logs',
  'src',
  'src/models',
  'src/agents',
  'src/orchestrator',
  'src/config',
  'src/api',
  'src/seed',
  'tests',
  'configs',
]

for (const dir of dirs) {
  await fs.mkdir(dir, { recursive: true })
  console.log(`ready: ${dir}`)
}

console.log('pm-zero v9.4 + ASCT directory structure ready.')
