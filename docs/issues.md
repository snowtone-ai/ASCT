# issues.md -- Failure Log and Self-Evolution

## Active Issues
| ID | Symptom | Context | Attempts | Status |
|---|---|---|---|---|
| - | - | - | - | - |

## Resolved (with root cause)
| ID | Root cause | Fix | Source URL | Promoted to |
|---|---|---|---|---|
| - | - | - | - | - |

## Promoted Rules
- (One line per durable rule moved into CLAUDE.md or docs/lessons.md)

## Hook-captured Failures
<!-- PostToolUseFailure hook appends entries below this line. -->

### Hook-captured failure (2026-06-21T17:29:26.210Z)
```
{"session_id":"6bd67af9-2c60-4d12-9ac4-c1e9c23bc6df","transcript_path":"C:\\Users\\chidj\\.claude\\projects\\C--Users-chidj-project-ASCT\\6bd67af9-2c60-4d12-9ac4-c1e9c23bc6df.jsonl","cwd":"C:\\Users\\chidj\\project\\ASCT","permission_mode":"default","effort":{"level":"medium"},"hook_event_name":"PostToolUseFailure","tool_name":"Bash","tool_input":{"command":"Get-ChildItem -Path \"C:\\Users\\chidj\\project\\ASCT\\src\" -Recurse | Where-Object { !$_.PSIsContainer } | Select-Object FullName | Sort-Object FullName","description":"List all files under src/"},"tool_use_id":"toolu_01UtMDNLV3FRPxE8xbLeA8Eq","error":"Exit code 127\n/usr/bin/bash: line 1: Get-ChildItem: command not found\n/usr/bin/bash: line 1: Where-Object: command not found\n/usr/bin/bash: line 1: Select-Object: command not found\n/usr/bin/bash: line 1: Sort-Object: command not found","is_interrupt":false,"duration_ms":402}

```
