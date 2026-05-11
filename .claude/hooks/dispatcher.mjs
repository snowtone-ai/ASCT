#!/usr/bin/env node
/**
 * .claude/hooks/dispatcher.mjs -- Claude Code unified hook handler
 * pm-zero v9.2
 */
import { readFile, appendFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { redact, warnHookFailure } from '../../scripts/lib/redact.mjs';

const args = process.argv.slice(2);
const eventFlag = args.find((a) => a.startsWith('--event='));
const event = eventFlag ? eventFlag.split('=')[1] : 'unknown';

async function handleSessionStart() {
  try {
    const files = ['docs/state.md', 'docs/decisions.md'];
    for (const f of files) {
      if (existsSync(f)) {
        const content = await readFile(f, 'utf-8');
        const lines = content.split('\n').slice(0, 30).join('\n');
        console.log(`--- ${f} (first 30 lines) ---`);
        console.log(lines);
      }
    }
  } catch (err) {
    warnHookFailure('SessionStart', err);
  }
}

async function handlePostToolUseFailure() {
  try {
    const input = await readFromStdin();
    const redacted = redact(input);
    const timestamp = new Date().toISOString();
    const entry = `\n### Hook-captured failure (${timestamp})\n\`\`\`\n${redacted}\n\`\`\`\n`;

    if (existsSync('docs/issues.md')) {
      await appendFile('docs/issues.md', entry);
    }
  } catch (err) {
    warnHookFailure('PostToolUseFailure', err);
  }
}

async function handleUserPromptSubmit() {
  try {
    if (existsSync('docs/state.md')) {
      const state = await readFile('docs/state.md', 'utf-8');
      const doneSection = state.match(/## Done\n([\s\S]*?)(?=\n## )/);
      if (doneSection) {
        const doneItems = doneSection[1].match(/- \[x\]/g);
        if (doneItems && doneItems.length > 0) {
          // Lightweight reminder only
        }
      }
    }
  } catch (err) {
    warnHookFailure('UserPromptSubmit', err);
  }
}

function readFromStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => (data += chunk));
    process.stdin.on('end', () => resolve(data));
    // If no stdin, resolve empty after timeout
    setTimeout(() => resolve(data), 100);
  });
}

switch (event) {
  case 'SessionStart':
    await handleSessionStart();
    break;
  case 'PostToolUseFailure':
    await handlePostToolUseFailure();
    break;
  case 'UserPromptSubmit':
    await handleUserPromptSubmit();
    break;
  default:
    console.log(`[dispatcher] Unknown event: ${event}`);
}
