#!/usr/bin/env node
import fs from 'node:fs/promises';

const dirs = [
  // pm-zero standard
  'docs',
  'scripts/lib',
  '.claude/hooks',
  '.claude/skills',
  'screenshots',
  'logs',
  // ASCT project structure
  'src',
  'src/models',
  'src/agents',
  'src/orchestrator',
  'src/config',
  'src/api',
  'src/seed',
  'tests',
  'tests/test_agents',
  'tests/test_orchestrator',
  'tests/test_api',
  'tests/test_config',
  'configs',
];

for (const dir of dirs) {
  await fs.mkdir(dir, { recursive: true });
  console.log(`created: ${dir}`);
}

console.log('pm-zero v10 + ASCT directory structure ready.');
