# ADF updater compatibility probe

Harmless public experimental fixtures. No ADF deployment configuration, data, or credentials. A stable skill launcher downloads one of two tiny Python runtimes with pre-pinned SHA-256 hashes. This tests host execution, outbound network, updates, and cache persistence; it is not a production updater.

Install `adf-updater-probe.zip` as a skill. Request the ADF updater probe. Repeat in another conversation to check cache behavior. Version selection is in `channel.json`.

## Signed release experiment

Install `adf-signed-updater-probe.zip` and request the ADF signed updater probe.
This separate launcher pins an experiment-only RSA public key, verifies signed
release metadata with the existing OpenSSL executable, and verifies the runtime
SHA-256 before execution. Future release hashes are not bundled in the skill.
Only Python standard-library modules and OpenSSL are required. The signing key
is kept outside this repository and is never distributed.

The default command checks `signed-channel.json`. Rejection experiments use
`--negative-test signature` or `--negative-test artifact`; they alter fetched
data in memory and must exit 1 without executing a runtime. Runtime fixtures
only print a version and random marker. No company data or configuration is
included. This is an authentication/compatibility experiment, not a production
updater: it has no key rotation, metadata expiry, or rollback/freeze protection.
GitHub raw-file caching can delay channel changes despite no-cache requests.
