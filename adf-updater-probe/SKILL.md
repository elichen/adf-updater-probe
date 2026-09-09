---
name: adf-updater-probe
description: Run the harmless ADF updater compatibility probe when the user explicitly requests an ADF updater probe or runtime update test. Downloads a tiny public Python fixture and reports its version, launcher hash, and cache status. Do not use for ordinary data questions.
---

Run the bundled `scripts/probe.py` with Python 3. Use its absolute path inside this skill directory. With no arguments it checks the public live release channel on every invocation, then downloads and runs the selected runtime only if its bundled SHA-256 matches. It stores the runtime under `~/.cache/adf-updater-probe-726491` and never accesses business data or credentials.

For an explicitly requested pinned release test, pass `--channel v1` or `--channel v2`. For the live update test use no arguments. Show the actual JSON output. Report execution or network failures accurately; never infer output from source code. Do not modify this skill or install dependencies. All code uses Python standard library.
