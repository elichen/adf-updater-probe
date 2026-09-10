---
name: adf-signed-updater-probe
description: Run the ADF signed updater experiment when asked to test independently published, authenticated runtime updates. Downloads a harmless public fixture after verifying its release signature. Separate from the older ADF updater probe.
---

Run this skill's `scripts/probe.py` using its absolute path with Python 3 and no arguments. It requires the existing `openssl` executable; report missing dependencies rather than installing them. It verifies release metadata against the bundled public key, checks the downloaded runtime hash, and executes the runtime. New releases need no skill reinstall. This experiment accesses only public synthetic fixtures, never business data or credentials.

Report actual command output and failures. Do not modify the installed skill. For explicitly requested rejection tests, `--negative-test signature` changes one signature byte in memory before verification and `--negative-test artifact` changes downloaded bytes before hash verification; both must reject without executing a runtime and use separate test directories. Neither option changes the public release or installed files.
