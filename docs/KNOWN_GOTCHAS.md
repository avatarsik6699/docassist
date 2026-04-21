# Known Gotchas

> Template memory file for derived projects.
> Capture recurring pitfalls that repeatedly waste time during coding, testing, or deploys.

## How To Use

- Add only issues that are likely to happen again.
- Prefer concrete symptoms, root cause, and the shortest reliable fix.
- Remove entries that are no longer relevant.

## Gotcha Log

### Docker-owned files and permission denied errors

- Symptoms: `EACCES`, `EPERM`, `Permission denied`, or `Read-only file system` while editing files or running local commands, often after Docker touched `.nuxt/`, `.output/`, `node_modules/.cache/`, or other bind-mounted artifacts.
- Root cause: a container wrote files to the host as `root`, so the normal user can no longer modify them.
- Fix: stop immediately and ask the user to repair ownership on the host. Recommended commands are `sudo chown -R $USER:$USER <path>` to keep the files or `sudo rm -rf <path>` to discard generated artifacts safely.
- Prevention: avoid ad hoc permission workarounds, and prefer cleaning generated artifacts rather than recursively loosening file permissions.
- Agent handoff: post the exact failing path and command, ask the user to fix ownership, then wait for the word `continue` before retrying. Never use `sudo`, `chmod -R 777`, or silent retries on your own.
